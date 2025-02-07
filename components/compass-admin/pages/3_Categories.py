import pandas as pd
import streamlit as st
from utils.api import APIClient
from utils.auth import login
from utils.common import (
    initialize_page,
    render_grid,
    show_success_toast,
    show_error_message,
    show_success_message,
    confirm_delete_dialog,
    format_dataframe_dates,
    handle_api_response,
    get_page_size_and_skip,
    COMMON_COLUMN_DEFS,
)

# Initialize session state
initialize_page("Categories", "📑", {
    "authenticated": False,
    "categories_page": 0,
    "categories_per_page": 100,
    "selected_category": None,
    "show_success_message": False,
    "show_error_message": None,
    "show_delete_success_toast": False,
    "page": 1
})

# Check authentication
if not st.session_state.authenticated:
    login()
    st.stop()

# Constants
COLUMN_DEFS = {
    "name": {"width": 150, "headerName": "Name"},
    "description": {"width": 300, "headerName": "Description"},
    "radar_quadrant": {"width": 120, "headerName": "Radar Quadrant"},
    "usage_count": {"width": 120, "headerName": "Usage Count"},
    **COMMON_COLUMN_DEFS  # Include common columns
}

def load_categories(skip=0, limit=10):
    """Load categories with pagination"""
    try:
        params = {"skip": skip, "limit": limit, "sort": "name"}
        response = APIClient.get("categories/", params)
        if response and isinstance(response, dict):
            return response.get("data", []), {
                "total": response.get("total", 0),
                "skip": response.get("skip", 0),
                "limit": response.get("limit", 10),
            }
    except Exception as e:
        show_error_message(f"Failed to load categories: {str(e)}")
    return [], {"total": 0, "skip": 0, "limit": 10}

def update_category(category_name, data):
    """Update category"""
    try:
        response = APIClient.put(f"categories/{category_name}", data)
        return handle_api_response(response, "Category updated successfully")
    except Exception as e:
        show_error_message(str(e))
        return False

def delete_category(category_name):
    """Delete category"""
    response = APIClient.delete(f"categories/{category_name}")
    if response and response.get("status_code") == 204:
        return
    else:
        return response.get("detail", "Unknown error occurred")

def render_category_form(category_data):
    """Render form for editing category"""
    with st.form("edit_category_form"):
        st.subheader("Edit Category")

        # Basic Information
        name = st.text_input(
            "Name*",
            value=category_data.get("name", ""),
            help="Category name"
        )
        description = st.text_area(
            "Description",
            value=category_data.get("description", ""),
            help="Category description"
        )
        
        # Add radar quadrant field
        radar_quadrant = st.number_input(
            "Radar Quadrant",
            min_value=-1,
            max_value=3,
            value=category_data.get("radar_quadrant", -1),
            help="Radar quadrant (-1,0,1,2,3)"
        )

        # Save Changes and Delete buttons
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            submitted = st.form_submit_button("Save Changes")
        with col2:
            delete_clicked = st.form_submit_button("Delete Category")

        if submitted:
            if not name:
                show_error_message("Category name is required")
                return

            update_data = {
                "name": name,
                "description": description if description else None,
                "radar_quadrant": int(radar_quadrant),
            }

            if update_category(category_data["name"], update_data):
                st.session_state.selected_category = None
                st.rerun()
        
        if st.session_state.show_success_message:
            show_success_message("Category updated successfully!")
            st.session_state.show_success_message = False

        if st.session_state.show_error_message:
            show_error_message(f"Failed to update category: {st.session_state.show_error_message}")
            st.session_state.show_error_message = None

    # Show delete confirmation dialog when delete button is clicked
    if delete_clicked:
        confirm_delete_dialog(f"category '{category_data['name']}'", 
                              lambda: delete_category(category_data["name"]), 
                              delete_success_callback)

def delete_success_callback():
    show_success_toast("Category deleted successfully!")
    st.session_state.show_delete_success_toast = True
    st.session_state.selected_category = None
    if "category_grid" in st.session_state:
        del st.session_state["category_grid"]
    st.rerun()

def render_add_category_form():
    """Render form for adding new category"""
    with st.form("add_category_form"):
        st.subheader("Add New Category")

        name = st.text_input("Name*", help="Category name")
        description = st.text_area("Description", help="Category description")
        radar_quadrant = st.number_input(
            "Radar Quadrant",
            min_value=-1,
            max_value=3,
            value=-1,
            help="Radar quadrant (-1,0,1,2,3)"
        )
        submitted = st.form_submit_button("Add Category")

        if st.session_state.show_success_message:
            show_success_message("Category added successfully!")
            st.session_state.show_success_message = False

        if st.session_state.show_error_message:
            show_error_message(f"Failed to add category: {st.session_state.show_error_message}")
            st.session_state.show_error_message = None

        if submitted:
            if not name:
                show_error_message("Category name is required")
                return

            category_data = {
                "name": name,
                "description": description if description else None,
                "radar_quadrant": int(radar_quadrant),
            }

            try:
                response = APIClient.post("categories/", category_data)
                if handle_api_response(response, "Category added successfully"):
                    st.rerun()
            except Exception as e:
                show_error_message(str(e))
                st.rerun()

def main():
    # Initialize page with common settings
    st.title("📑 Categories")

    # Show toast message if deletion was successful
    if st.session_state.show_delete_success_toast:
        show_success_toast("Category deleted successfully!")
        st.session_state.show_delete_success_toast = False

    # Create tabs
    list_tab, add_tab = st.tabs(["Categories List", "Add New Category"])

    with list_tab:
        page_size, skip = get_page_size_and_skip()
        categories, meta = load_categories(skip=skip, limit=page_size)

        if categories:
            # Create DataFrame with explicit column order
            df = pd.DataFrame(categories)[COLUMN_DEFS.keys()]
            df = format_dataframe_dates(df)  # Using default date columns

            # Render grid
            grid_response = render_grid(df, COLUMN_DEFS, "category_grid", page_size)
            selected_rows = grid_response.get("selected_rows", [])

            # Show edit form only if we have selected rows and no deletion just happened
            if selected_rows is not None and not st.session_state.show_delete_success_toast:
                selected_category = selected_rows.iloc[0].to_dict()
                st.session_state.selected_category = selected_category
                render_category_form(selected_category)
        else:
            st.info("No categories found")

    with add_tab:
        render_add_category_form()

if __name__ == "__main__":
    main()
