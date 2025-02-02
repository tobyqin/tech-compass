import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { MenuItem, MessageService } from 'primeng/api';
import { DialogService } from 'primeng/dynamicdialog';

import { BreadcrumbModule } from 'primeng/breadcrumb';
import { ButtonModule } from 'primeng/button';
import { ChipsModule } from 'primeng/chips';
import { DropdownModule } from 'primeng/dropdown';
import { InputTextModule } from 'primeng/inputtext';
import { InputTextareaModule } from 'primeng/inputtextarea';
import { MessagesModule } from 'primeng/messages';

import { CategoryService } from '../../core/services/category.service';
import { DepartmentService } from '../../core/services/department.service';
import { SolutionService } from '../../core/services/solution.service';
import { AuthService } from '../../core/services/auth.service';
import { LoginDialogComponent } from '../../core/components/login-dialog/login-dialog.component';

@Component({
  selector: 'app-submit-solution',
  templateUrl: './submit-solution.component.html',
  styleUrls: ['./submit-solution.component.scss'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    RouterModule,
    BreadcrumbModule,
    ButtonModule,
    ChipsModule,
    DropdownModule,
    InputTextModule,
    InputTextareaModule,
    MessagesModule
  ],
  providers: [
    MessageService,
    DialogService
  ]
})
export class SubmitSolutionComponent implements OnInit {
  categories: { name: string }[] = [];
  departments: string[] = [];
  submitting = false;
  isLoggedIn = false;
  
  stageOptions = [
    { label: 'DEVELOPING', value: 'DEVELOPING' },
    { label: 'UAT', value: 'UAT' },
    { label: 'PRODUCTION', value: 'PRODUCTION' },
    { label: 'DEPRECATED', value: 'DEPRECATED' },
    { label: 'RETIRED', value: 'RETIRED' }
  ];
  
  radarStatusOptions = [
    { label: 'ADOPT', value: 'ADOPT' },
    { label: 'TRIAL', value: 'TRIAL' },
    { label: 'ASSESS', value: 'ASSESS' },
    { label: 'HOLD', value: 'HOLD' }
  ];
  
  recommendStatusOptions = [
    { label: 'BUY', value: 'BUY' },
    { label: 'HOLD', value: 'HOLD' },
    { label: 'SELL', value: 'SELL' }
  ];
  
  solutionForm: FormGroup;
  
  constructor(
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    private categoryService: CategoryService,
    private departmentService: DepartmentService,
    private solutionService: SolutionService,
    private messageService: MessageService,
    private dialogService: DialogService,
    private authService: AuthService
  ) {
    this.solutionForm = this.fb.group({
      name: ['', Validators.required],
      description: ['', Validators.required],
      category: ['', Validators.required],
      logo: [''],
      department: ['', Validators.required],
      team: ['', Validators.required],
      team_email: ['', [Validators.required, Validators.email]],
      maintainer_id: ['', Validators.required],
      maintainer_name: ['', Validators.required],
      maintainer_email: ['', [Validators.required, Validators.email]],
      official_website: [''],
      documentation_url: [''],
      demo_url: [''],
      version: ['', Validators.required],
      tags: [[]],
      pros: [''],
      cons: [''],
      stage: ['', Validators.required],
      radar_status: ['', Validators.required],
      recommend_status: ['', Validators.required]
    });
  }
  
  ngOnInit() {
    this.loadCategories();
    this.loadDepartments();
    this.authService.currentUser$.subscribe(user => {
      this.isLoggedIn = !!user;
    });
  }

  private loadCategories() {
    this.categoryService.getCategories().subscribe(response => {
      if (response.success) {
        this.categories = response.data;
        
        // Set category from query param if available
        this.route.queryParams.subscribe(params => {
          if (params['category']) {
            this.solutionForm.patchValue({ category: params['category'] });
          }
        });
      }
    });
  }

  private loadDepartments() {
    this.departmentService.getDepartments().subscribe(response => {
      if (response.success) {
        this.departments = response.data;
      }
    });
  }

  onSubmit() {
    if (this.solutionForm.valid) {
      this.submitting = true;
      
      // Convert multiline text to arrays
      const formValue = this.solutionForm.value;
      const pros = formValue.pros?.split('\n').filter((line: string) => line.trim()) || [];
      const cons = formValue.cons?.split('\n').filter((line: string) => line.trim()) || [];
      
      const solution = {
        ...formValue,
        pros,
        cons
      };

      this.solutionService.createSolution(solution).subscribe({
        next: (response) => {
          this.router.navigate(['submit-solution/success']);
        },
        error: (error) => {
          this.messageService.add({
            severity: 'error',
            summary: 'Error',
            detail: error.error?.detail || 'Failed to create solution'
          });
          this.submitting = false;
        }
      });
    }
  }

  showLoginDialog() {
    const ref = this.dialogService.open(LoginDialogComponent, {
      width: '400px',
      header: ' ',
      contentStyle: { padding: 0 },
      baseZIndex: 1000,
      style: {
        'box-shadow': '0 4px 20px rgba(0, 0, 0, 0.1)'
      }
    });

    ref.onClose.subscribe((success: boolean) => {
      if (success) {
        this.messageService.add({
          severity: 'success',
          summary: 'Success',
          detail: 'You are now logged in'
        });
      }
    });
  }
}
