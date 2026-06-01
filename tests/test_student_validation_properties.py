"""Property-based tests for Student data model validation.

**Validates: Requirements 5.1, 5.2, 5.3, 5.4**
"""

import pytest
from hypothesis import given, strategies as st, assume
from pydantic import ValidationError

from src.models.student import StudentBase, StudentCreate, StudentUpdate


# Strategies for generating valid and invalid data

valid_full_names = st.text(
    alphabet=st.characters(blacklist_categories=('Cc', 'Cs')),
    min_size=1,
    max_size=100
)

valid_ages = st.integers(min_value=4, max_value=25)

valid_classes = st.text(
    alphabet=st.characters(blacklist_categories=('Cc', 'Cs')),
    min_size=1,
    max_size=20
)

valid_genders = st.sampled_from(['Male', 'Female', 'Other'])

invalid_full_names = st.just("")

invalid_ages_too_low = st.integers(max_value=3)
invalid_ages_too_high = st.integers(min_value=26)

invalid_classes = st.just("")

invalid_genders = st.text(
    alphabet=st.characters(blacklist_categories=('Cc', 'Cs')),
    min_size=1
).filter(lambda x: x not in ['Male', 'Female', 'Other'])


class TestFieldSpecificValidation:
    """Property tests for field-specific validation.
    
    **Property 14: Field-Specific Validation**
    **Validates: Requirements 5.1, 5.2, 5.3, 5.4**
    
    For any input value V for field F (where F is one of: fullName, age, class, gender),
    the validation function validateField(F, V) shall:
    1. Return success for all values V that satisfy field F's validation rules
    2. Return error for all values V that violate field F's validation rules
    3. Provide specific error messages identifying the rule violation
    4. Apply validation rules consistently across all operations (create, update)
    """
    
    @given(valid_full_names, valid_ages, valid_classes, valid_genders)
    def test_valid_student_creation_with_valid_inputs(self, name, age, class_, gender):
        """Test that StudentCreate accepts all valid inputs.
        
        For any valid student data, StudentCreate should accept it without errors.
        """
        student = StudentCreate(
            full_name=name,
            age=age,
            class_=class_,
            gender=gender
        )
        assert student.full_name == name
        assert student.age == age
        assert student.class_ == class_
        assert student.gender == gender
    
    @given(valid_full_names, valid_ages, valid_classes, valid_genders)
    def test_valid_student_base_with_valid_inputs(self, name, age, class_, gender):
        """Test that StudentBase accepts all valid inputs.
        
        For any valid student data, StudentBase should accept it without errors.
        """
        student = StudentBase(
            full_name=name,
            age=age,
            class_=class_,
            gender=gender
        )
        assert student.full_name == name
        assert student.age == age
        assert student.class_ == class_
        assert student.gender == gender
    
    @given(invalid_full_names)
    def test_invalid_full_name_rejected(self, name):
        """Test that invalid full_name values are rejected.
        
        For any invalid full_name, StudentCreate should raise ValidationError.
        """
        with pytest.raises(ValidationError):
            StudentCreate(
                full_name=name,
                age=15,
                class_="10A",
                gender="Male"
            )
    
    @given(invalid_ages_too_low)
    def test_invalid_age_too_low_rejected(self, age):
        """Test that ages below 4 are rejected.
        
        For any age < 4, StudentCreate should raise ValidationError.
        """
        with pytest.raises(ValidationError):
            StudentCreate(
                full_name="John Doe",
                age=age,
                class_="10A",
                gender="Male"
            )
    
    @given(invalid_ages_too_high)
    def test_invalid_age_too_high_rejected(self, age):
        """Test that ages above 25 are rejected.
        
        For any age > 25, StudentCreate should raise ValidationError.
        """
        with pytest.raises(ValidationError):
            StudentCreate(
                full_name="John Doe",
                age=age,
                class_="10A",
                gender="Male"
            )
    
    @given(invalid_classes)
    def test_invalid_class_rejected(self, class_):
        """Test that invalid class values are rejected.
        
        For any invalid class, StudentCreate should raise ValidationError.
        """
        with pytest.raises(ValidationError):
            StudentCreate(
                full_name="John Doe",
                age=15,
                class_=class_,
                gender="Male"
            )
    
    @given(invalid_genders)
    def test_invalid_gender_rejected(self, gender):
        """Test that invalid gender values are rejected.
        
        For any gender not in ['Male', 'Female', 'Other'], StudentCreate should raise ValidationError.
        """
        with pytest.raises(ValidationError):
            StudentCreate(
                full_name="John Doe",
                age=15,
                class_="10A",
                gender=gender
            )
    
    @given(valid_full_names, valid_ages, valid_classes, valid_genders)
    def test_validation_consistency_across_models(self, name, age, class_, gender):
        """Test that validation is consistent across StudentBase, StudentCreate, and StudentUpdate.
        
        For any valid data, all models should accept it.
        """
        # Should work in StudentBase
        base = StudentBase(
            full_name=name,
            age=age,
            class_=class_,
            gender=gender
        )
        assert base.full_name == name
        
        # Should work in StudentCreate
        create = StudentCreate(
            full_name=name,
            age=age,
            class_=class_,
            gender=gender
        )
        assert create.full_name == name
        
        # Should work in StudentUpdate
        update = StudentUpdate(
            full_name=name,
            age=age,
            class_=class_,
            gender=gender
        )
        assert update.full_name == name
    
    @given(valid_full_names)
    def test_full_name_validation_in_update(self, name):
        """Test that full_name validation works in StudentUpdate.
        
        For any valid full_name, StudentUpdate should accept it.
        """
        update = StudentUpdate(full_name=name)
        assert update.full_name == name
    
    @given(valid_ages)
    def test_age_validation_in_update(self, age):
        """Test that age validation works in StudentUpdate.
        
        For any valid age, StudentUpdate should accept it.
        """
        update = StudentUpdate(age=age)
        assert update.age == age
    
    @given(valid_classes)
    def test_class_validation_in_update(self, class_):
        """Test that class validation works in StudentUpdate.
        
        For any valid class, StudentUpdate should accept it.
        """
        update = StudentUpdate(class_=class_)
        assert update.class_ == class_
    
    @given(valid_genders)
    def test_gender_validation_in_update(self, gender):
        """Test that gender validation works in StudentUpdate.
        
        For any valid gender, StudentUpdate should accept it.
        """
        update = StudentUpdate(gender=gender)
        assert update.gender == gender
    
    @given(invalid_ages_too_low)
    def test_invalid_age_in_update_rejected(self, age):
        """Test that invalid ages are rejected in StudentUpdate.
        
        For any age < 4, StudentUpdate should raise ValidationError.
        """
        with pytest.raises(ValidationError):
            StudentUpdate(age=age)
    
    @given(invalid_ages_too_high)
    def test_invalid_age_in_update_too_high_rejected(self, age):
        """Test that ages > 25 are rejected in StudentUpdate.
        
        For any age > 25, StudentUpdate should raise ValidationError.
        """
        with pytest.raises(ValidationError):
            StudentUpdate(age=age)
    
    @given(invalid_genders)
    def test_invalid_gender_in_update_rejected(self, gender):
        """Test that invalid genders are rejected in StudentUpdate.
        
        For any gender not in ['Male', 'Female', 'Other'], StudentUpdate should raise ValidationError.
        """
        with pytest.raises(ValidationError):
            StudentUpdate(gender=gender)
    
    @given(st.text(min_size=101, max_size=200))
    def test_full_name_max_length_enforced(self, name):
        """Test that full_name max length is enforced.
        
        For any full_name with length > 100, StudentCreate should raise ValidationError.
        """
        with pytest.raises(ValidationError):
            StudentCreate(
                full_name=name,
                age=15,
                class_="10A",
                gender="Male"
            )
    
    @given(st.text(min_size=21, max_size=50))
    def test_class_max_length_enforced(self, class_):
        """Test that class max length is enforced.
        
        For any class with length > 20, StudentCreate should raise ValidationError.
        """
        assume(class_.strip())  # Ensure it's not just whitespace
        with pytest.raises(ValidationError):
            StudentCreate(
                full_name="John Doe",
                age=15,
                class_=class_,
                gender="Male"
            )
    
    @given(valid_full_names, valid_ages, valid_classes, valid_genders)
    def test_all_valid_fields_together(self, name, age, class_, gender):
        """Test that all valid fields work together.
        
        For any combination of valid fields, StudentCreate should accept them.
        """
        student = StudentCreate(
            full_name=name,
            age=age,
            class_=class_,
            gender=gender
        )
        assert student.full_name == name
        assert student.age == age
        assert student.class_ == class_
        assert student.gender == gender
    
    def test_gender_case_sensitive(self):
        """Test that gender validation is case-sensitive.
        
        Gender values should be exactly 'Male', 'Female', or 'Other'.
        """
        # Valid cases
        for gender in ['Male', 'Female', 'Other']:
            student = StudentCreate(
                full_name="John Doe",
                age=15,
                class_="10A",
                gender=gender
            )
            assert student.gender == gender
        
        # Invalid cases (different case)
        for gender in ['male', 'MALE', 'female', 'FEMALE', 'other', 'OTHER']:
            with pytest.raises(ValidationError):
                StudentCreate(
                    full_name="John Doe",
                    age=15,
                    class_="10A",
                    gender=gender
                )
    
    @given(st.text(min_size=1, max_size=100).filter(lambda x: x.strip()))
    def test_class_whitespace_handling(self, class_):
        """Test that class whitespace is handled correctly.
        
        Class values with leading/trailing whitespace should be stripped.
        """
        student = StudentCreate(
            full_name="John Doe",
            age=15,
            class_=class_,
            gender="Male"
        )
        # Class should be stripped
        assert student.class_ == class_.strip()
    
    @given(valid_full_names, valid_ages, valid_classes, valid_genders)
    def test_partial_update_with_valid_fields(self, name, age, class_, gender):
        """Test that StudentUpdate accepts partial valid data.
        
        For any valid field value, StudentUpdate should accept it even if other fields are missing.
        """
        # Update with just name
        update1 = StudentUpdate(full_name=name)
        assert update1.full_name == name
        
        # Update with just age
        update2 = StudentUpdate(age=age)
        assert update2.age == age
        
        # Update with just class
        update3 = StudentUpdate(class_=class_)
        assert update3.class_ == class_
        
        # Update with just gender
        update4 = StudentUpdate(gender=gender)
        assert update4.gender == gender
