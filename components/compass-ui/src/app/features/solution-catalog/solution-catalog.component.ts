import { Component, OnInit, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SolutionService } from '../../core/services/solution.service';
import { SolutionCardComponent } from '../../shared/components/solution-card/solution-card.component';
import { Solution } from '../../shared/interfaces/solution.interface';
import { CategoryService, Category } from '../../core/services/category.service';
import { DepartmentService } from '../../core/services/department.service';

// PrimeNG imports
import { DropdownModule } from 'primeng/dropdown';
import { MultiSelectModule } from 'primeng/multiselect';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { MessageModule } from 'primeng/message';
import { TooltipModule } from 'primeng/tooltip';

interface SolutionFilters {
  category?: string;
  department?: string;
  team?: string;
  recommend_status?: 'BUY' | 'HOLD' | 'SELL';
  radar_status?: 'ADOPT' | 'TRIAL' | 'ASSESS' | 'HOLD';
  stage?: 'DEVELOPING' | 'UAT' | 'PRODUCTION' | 'DEPRECATED' | 'RETIRED';
  sort: string;
}

interface SolutionParams extends SolutionFilters {
  skip: number;
  limit: number;
  [key: string]: string | number | undefined;
}

interface CategoryOption {
  label: string;
  value: string | null;
  title?: string; // For tooltip
}

interface DropdownOption {
  label: string;
  value: string | null;
}

@Component({
  selector: 'app-solution-catalog',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    SolutionCardComponent,
    DropdownModule,
    MultiSelectModule,
    ProgressSpinnerModule,
    MessageModule,
    TooltipModule
  ],
  template: `
<div class="solutions-container">
  <div class="filters-header">
    <h2>Solution Catalog</h2>
    <div class="filters-row">
      <div class="left-group">
        <div class="filter-item">
          <label>Sort By</label>
          <p-dropdown 
            [options]="sortOptions" 
            [(ngModel)]="filters.sort"
            (onChange)="onFilterChange()"
            [style]="{'width':'100%'}"
            placeholder="Select Sort Order">
          </p-dropdown>
        </div>

        <div class="filter-item">
          <label>Category</label>
          <p-dropdown 
            [options]="categoryOptions" 
            [(ngModel)]="filters.category"
            (onChange)="onFilterChange()"
            [style]="{'width':'100%'}"
            [showClear]="true"
            [tooltip]="getSelectedCategoryTooltip()"
            tooltipPosition="bottom"
            placeholder="Select Category">
            <ng-template pTemplate="item" let-option>
              <div [attr.title]="option.title">{{ option.label }}</div>
            </ng-template>
          </p-dropdown>
        </div>

        <div class="filter-item">
          <label>Department</label>
          <p-dropdown 
            [options]="departmentOptions" 
            [(ngModel)]="filters.department"
            (onChange)="onFilterChange()"
            [style]="{'width':'100%'}"
            [showClear]="true"
            placeholder="Select Department">
          </p-dropdown>
        </div>
      </div>

      <div class="right-group">
        <div class="filter-item">
          <label>Recommend Status</label>
          <p-dropdown 
            [options]="recommendStatusOptions" 
            [(ngModel)]="filters.recommend_status"
            (onChange)="onFilterChange()"
            [style]="{'width':'100%'}"
            [showClear]="true"
            placeholder="Select Status">
          </p-dropdown>
        </div>

        <div class="filter-item">
          <label>Radar Status</label>
          <p-dropdown 
            [options]="radarStatusOptions" 
            [(ngModel)]="filters.radar_status"
            (onChange)="onFilterChange()"
            [style]="{'width':'100%'}"
            [showClear]="true"
            placeholder="Select Status">
          </p-dropdown>
        </div>

        <div class="filter-item">
          <label>Stage</label>
          <p-dropdown 
            [options]="stageOptions" 
            [(ngModel)]="filters.stage"
            (onChange)="onFilterChange()"
            [style]="{'width':'100%'}"
            [showClear]="true"
            placeholder="Select Stage">
          </p-dropdown>
        </div>
      </div>
    </div>
  </div>

  <div class="solutions-content">
    <div class="solutions-grid" *ngIf="!loading || solutions.length > 0">
      <app-solution-card 
        *ngFor="let solution of solutions" 
        [solution]="solution">
      </app-solution-card>
    </div>

    <div class="loading-more" *ngIf="loadingMore">
      <p-progressSpinner></p-progressSpinner>
      <p>Loading more solutions...</p>
    </div>

    <div class="loading-state" *ngIf="loading && solutions.length === 0">
      <p-progressSpinner></p-progressSpinner>
      <p>Loading solutions...</p>
    </div>

    <div class="error-state" *ngIf="error">
      <p-message severity="error" [text]="error"></p-message>
    </div>
  </div>
</div>
  `,
  styleUrls: ['./solution-catalog.component.scss'],
  providers: [CategoryService, DepartmentService]
})
export class SolutionCatalogComponent implements OnInit {
  solutions: Solution[] = [];
  loading = true;
  loadingMore = false;
  error: string | null = null;
  totalRecords = 0;
  
  // Pagination
  currentPage = 0;
  initialPageSize = 9;
  loadMoreSize = 6;
  hasMore = true;

  // Filters
  filters: SolutionFilters = {
    sort: 'name'
  };

  categoryOptions: CategoryOption[] = [
    { label: 'All', value: null }
  ];

  departmentOptions: DropdownOption[] = [
    { label: 'All', value: null }
  ];

  // Filter options
  recommendStatusOptions = [
    { label: 'Buy', value: 'BUY' },
    { label: 'Hold', value: 'HOLD' },
    { label: 'Sell', value: 'SELL' }
  ];

  radarStatusOptions = [
    { label: 'Adopt', value: 'ADOPT' },
    { label: 'Trial', value: 'TRIAL' },
    { label: 'Assess', value: 'ASSESS' },
    { label: 'Hold', value: 'HOLD' }
  ];

  stageOptions = [
    { label: 'Developing', value: 'DEVELOPING' },
    { label: 'UAT', value: 'UAT' },
    { label: 'Production', value: 'PRODUCTION' },
    { label: 'Deprecated', value: 'DEPRECATED' },
    { label: 'Retired', value: 'RETIRED' }
  ];

  sortOptions = [
    { label: 'Newest First', value: '-created_at' },
    { label: 'Oldest First', value: 'created_at' },
    { label: 'Name A-Z', value: 'name' },
    { label: 'Name Z-A', value: '-name' }
  ];

  constructor(
    private solutionService: SolutionService,
    private categoryService: CategoryService,
    private departmentService: DepartmentService
  ) {}

  ngOnInit(): void {
    this.loadCategories();
    this.loadDepartments();
    this.loadSolutions();
  }

  @HostListener('window:scroll', ['$event'])
  onScroll(): void {
    if (this.isNearBottom() && !this.loadingMore && this.hasMore) {
      this.loadMore();
    }
  }

  private isNearBottom(): boolean {
    const threshold = 200;
    const position = window.scrollY + window.innerHeight;
    const height = document.documentElement.scrollHeight;
    return position > height - threshold;
  }

  onFilterChange(): void {
    this.solutions = [];
    this.currentPage = 0;
    this.hasMore = true;
    this.loadSolutions();
  }

  private loadMore(): void {
    this.loadingMore = true;
    this.currentPage++;
    
    const params: SolutionParams = {
      skip: this.currentPage * this.loadMoreSize,
      limit: this.loadMoreSize,
      ...this.filters
    };

    // Remove any null or undefined values
    Object.keys(params).forEach(key => {
      if (params[key] === null || params[key] === undefined) {
        delete params[key];
      }
    });

    this.solutionService.getSolutions(params).subscribe({
      next: (response) => {
        this.solutions = [...this.solutions, ...response.data];
        this.totalRecords = response.total;
        this.hasMore = this.solutions.length < this.totalRecords;
        this.loadingMore = false;
      },
      error: (error) => {
        this.error = 'Failed to load more solutions';
        this.loadingMore = false;
        console.error('Error loading solutions:', error);
      }
    });
  }

  private loadSolutions(): void {
    this.loading = true;
    const params: SolutionParams = {
      skip: 0,
      limit: this.initialPageSize,
      ...this.filters
    };

    // Remove any null or undefined values
    Object.keys(params).forEach(key => {
      if (params[key] === null || params[key] === undefined) {
        delete params[key];
      }
    });

    this.solutionService.getSolutions(params).subscribe({
      next: (response) => {
        this.solutions = response.data;
        this.totalRecords = response.total;
        this.hasMore = this.solutions.length < this.totalRecords;
        this.loading = false;
      },
      error: (error) => {
        this.error = 'Failed to load solutions';
        this.loading = false;
        console.error('Error loading solutions:', error);
      }
    });
  }

  private loadCategories(): void {
    this.categoryService.getCategories().subscribe({
      next: (response) => {
        const categories = response.data.map(category => ({
          label: `${category.name} (${category.usage_count})`,
          value: category.name,
          title: `${category.name} - Used in ${category.usage_count} solution${category.usage_count !== 1 ? 's' : ''}`
        }));
        this.categoryOptions = [
          { label: 'All', value: null },
          ...categories.sort((a, b) => a.label.localeCompare(b.label))
        ];
      },
      error: (error: Error) => {
        console.error('Error loading categories:', error);
      }
    });
  }

  private loadDepartments(): void {
    this.departmentService.getDepartments().subscribe({
      next: (response) => {
        const departments = response.data.map(dept => ({
          label: dept,
          value: dept
        }));
        this.departmentOptions = [
          { label: 'All', value: null },
          ...departments.sort((a, b) => a.label.localeCompare(b.label))
        ];
      },
      error: (error: Error) => {
        console.error('Error loading departments:', error);
      }
    });
  }

  getSelectedCategoryTooltip(): string {
    if (!this.filters.category) return '';
    const selectedOption = this.categoryOptions.find(opt => opt.value === this.filters.category);
    return selectedOption?.title || '';
  }
} 