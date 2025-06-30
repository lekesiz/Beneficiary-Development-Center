"""Simple test to verify Course module works."""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_course_imports():
    """Test that Course-related imports work."""
    try:
        from app.models.course import Course, CourseStatus, CourseFormat, DifficultyLevel
        from app.schemas.course import CourseCreateSchema, CourseUpdateSchema
        from app.services.course_service import CourseService

        print("✓ All Course imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_course_model():
    """Test Course model creation."""
    from app.models.course import Course, CourseStatus, CourseFormat, DifficultyLevel

    course = Course(
        tenant_id=1,
        program_id=1,
        title="Test Course",
        format=CourseFormat.LECTURE,
        difficulty_level=DifficultyLevel.BEGINNER,
        status=CourseStatus.DRAFT,
        created_by=1,
    )

    assert course.title == "Test Course"
    assert course.format == CourseFormat.LECTURE
    assert course.difficulty_level == DifficultyLevel.BEGINNER
    assert course.status == CourseStatus.DRAFT
    print("✓ Course model creation successful")
    return True


def test_course_schema():
    """Test Course schema validation."""
    from app.schemas.course import CourseCreateSchema

    schema = CourseCreateSchema()

    # Valid data
    valid_data = {"title": "Test Course", "program_id": 1}

    result = schema.load(valid_data)
    assert result["title"] == "Test Course"
    print("✓ Course schema validation successful")


def test_course_service():
    """Test Course service class."""
    from app.services.course_service import CourseService
    from sqlalchemy.orm import Session

    # Just test that the service can be instantiated
    # (without a real database session)
    service = CourseService(None)  # type: ignore
    assert service is not None
    print("✓ Course service instantiation successful")


if __name__ == "__main__":
    print("Running Course module tests...\n")

    tests = [test_course_imports, test_course_model, test_course_schema, test_course_service]

    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")

    print(f"\nPassed {passed}/{len(tests)} tests")

    if passed == len(tests):
        print("\n✓ All Course module tests passed!")
        exit(0)
    else:
        print("\n✗ Some tests failed")
        exit(1)
