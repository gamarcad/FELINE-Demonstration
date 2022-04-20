import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ParametersImpactComponent } from './parameters-impact.component';

describe('ParametersImpactComponent', () => {
  let component: ParametersImpactComponent;
  let fixture: ComponentFixture<ParametersImpactComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ParametersImpactComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ParametersImpactComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
