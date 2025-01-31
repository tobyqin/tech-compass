import { Component, OnInit, HostListener } from '@angular/core';
import { Router } from '@angular/router';
import { CategoryService } from './category.service';
import { Category } from './category.interface';

@Component({
  selector: 'tc-categories',
  templateUrl: 'categories.component.html',
  styleUrls: ['categories.component.scss']
})
export class CategoriesComponent implements OnInit {
  categories: Category[] = [];
  loading = false;
  allLoaded = false;
  private skip = 0;
  private readonly limit = 20;

  constructor(
    private categoryService: CategoryService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadCategories();
  }

  @HostListener('window:scroll', ['$event'])
  onScroll(): void {
    if (this.loading || this.allLoaded) return;

    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;
    const scrollTop = window.scrollY || document.documentElement.scrollTop;

    if (windowHeight + scrollTop >= documentHeight - 200) {
      this.loadCategories();
    }
  }

  private loadCategories(): void {
    if (this.loading || this.allLoaded) return;

    this.loading = true;
    this.categoryService.getCategories(this.skip, this.limit).subscribe({
      next: (response) => {
        if (response.success) {
          this.categories = [...this.categories, ...response.data];
          this.skip += this.limit;
          this.allLoaded = response.data.length < this.limit;
        }
      },
      error: (error) => {
        console.error('Error loading categories:', error);
      },
      complete: () => {
        this.loading = false;
      }
    });
  }

  navigateToSolutions(category: Category): void {
    this.router.navigate(['/solution-catalog'], {
      queryParams: { category: category.name }
    });
  }
} 