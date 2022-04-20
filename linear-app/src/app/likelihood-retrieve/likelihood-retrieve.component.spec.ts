import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LikelihoodRetrieveComponent } from './likelihood-retrieve.component';

describe('LikelihoodRetrieveComponent', () => {
  let component: LikelihoodRetrieveComponent;
  let fixture: ComponentFixture<LikelihoodRetrieveComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ LikelihoodRetrieveComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(LikelihoodRetrieveComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
