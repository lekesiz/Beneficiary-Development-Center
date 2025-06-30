"""Database seeding utilities."""

import random
from datetime import datetime, timedelta
from faker import Faker
from app import create_app, db
from app.models.user import User, Role
from app.models.tenant import Tenant
from app.models.program import Program, ProgramStatus
from app.models.course import Course
from app.models.beneficiary import Beneficiary
from app.models.enrollment import Enrollment
from app.models.evaluation import Evaluation, Question, QuestionType
from werkzeug.security import generate_password_hash

fake = Faker()


def create_tenants():
    """Create sample tenants."""
    tenants = []

    # Default tenant
    default_tenant = Tenant(
        name="Default Organization",
        domain="default.bdc.local",
        settings={"theme": "default", "language": "en", "timezone": "UTC"},
        is_active=True,
    )
    tenants.append(default_tenant)

    # Additional sample tenants
    for i in range(2):
        tenant = Tenant(
            name=fake.company(),
            domain=f"tenant{i+1}.bdc.local",
            settings={
                "theme": "default",
                "language": random.choice(["en", "fr", "es"]),
                "timezone": random.choice(["UTC", "America/New_York", "Europe/Paris"]),
            },
            is_active=True,
        )
        tenants.append(tenant)

    db.session.add_all(tenants)
    db.session.commit()
    return tenants


def create_roles():
    """Create system roles."""
    roles = []
    
    # Create system roles
    role_definitions = [
        {
            "name": "super_admin",
            "description": "Super Administrator with full system access",
            "permissions": Role.get_default_permissions("super_admin"),
            "is_system": True
        },
        {
            "name": "admin",
            "description": "Administrator with tenant management access",
            "permissions": Role.get_default_permissions("admin"),
            "is_system": True
        },
        {
            "name": "trainer",
            "description": "Trainer with program and beneficiary management",
            "permissions": Role.get_default_permissions("trainer"),
            "is_system": True
        },
        {
            "name": "student",
            "description": "Student with basic access",
            "permissions": Role.get_default_permissions("student"),
            "is_system": True
        }
    ]
    
    for role_def in role_definitions:
        role = Role(**role_def)
        roles.append(role)
    
    db.session.add_all(roles)
    db.session.commit()
    return roles


def create_users(tenants, roles):
    """Create sample users."""
    users = []
    role_names = ["admin", "trainer", "student"]
    
    # Get role objects
    admin_role = next(r for r in roles if r.name == "admin")
    trainer_role = next(r for r in roles if r.name == "trainer")
    student_role = next(r for r in roles if r.name == "student")

    # Create admin
    admin_user = User(
        email="admin@bdc.local",
        password_hash=generate_password_hash("admin123"),
        first_name="Super",
        last_name="Admin",
        tenant_id=tenants[0].id,
        is_active=True,
        is_verified=True,
    )
    admin_user.roles.append(admin_role)
    users.append(admin_user)
    
    # Create trainer
    trainer_user = User(
        email="trainer@bdc.local",
        password_hash=generate_password_hash("trainer123"),
        first_name="John",
        last_name="Trainer",
        tenant_id=tenants[0].id,
        is_active=True,
        is_verified=True,
    )
    trainer_user.roles.append(trainer_role)
    users.append(trainer_user)
    
    # Create student
    student_user = User(
        email="student@bdc.local",
        password_hash=generate_password_hash("student123"),
        first_name="Jane",
        last_name="Student", 
        tenant_id=tenants[0].id,
        is_active=True,
        is_verified=True,
    )
    student_user.roles.append(student_role)
    users.append(student_user)

    db.session.add_all(users)
    db.session.commit()
    return users


def create_programs(tenants, users):
    """Create sample programs."""
    programs = []
    categories = ["education", "vocational", "health", "social", "economic"]

    for tenant in tenants:
        managers = [u for u in users if u.tenant_id == tenant.id and u.has_role("admin")]

        for i in range(random.randint(3, 8)):
            start_date = fake.date_between(start_date="-30d", end_date="+180d")
            end_date = start_date + timedelta(days=random.randint(30, 365))

            program = Program(
                tenant_id=tenant.id,
                code=f"PRG-{tenant.id}-{i+1:03d}",
                title=f"{fake.catch_phrase()} Program",
                description=fake.text(max_nb_chars=500),
                status=random.choice([ProgramStatus.DRAFT, ProgramStatus.ACTIVE, ProgramStatus.COMPLETED]),
                start_date=start_date,
                end_date=end_date,
                objectives=[fake.sentence() for _ in range(3)],
                tags=[random.choice(categories)],
                requirements={
                    "min_age": random.randint(16, 25),
                    "max_age": random.randint(35, 65),
                    "requirements": [fake.sentence() for _ in range(3)],
                },
                created_by=random.choice(managers).id if managers else users[0].id,
            )
            programs.append(program)

    db.session.add_all(programs)
    db.session.commit()
    return programs


def create_courses(programs, users):
    """Create sample courses."""
    courses = []
    course_types = ["lecture", "workshop", "practical", "online", "hybrid"]

    for program in programs:
        instructors = [u for u in users if u.tenant_id == program.tenant_id and u.has_role("trainer")]

        for i in range(random.randint(2, 6)):
            course = Course(
                tenant_id=program.tenant_id,
                program_id=program.id,
                code=f"CRS-{program.id}-{i+1:03d}",
                name=f"{fake.catch_phrase()} Course",
                description=fake.text(max_nb_chars=500),
                course_type=random.choice(course_types),
                credits=random.randint(1, 4),
                duration_hours=random.randint(20, 120),
                max_students=random.randint(20, 50),
                instructor_id=random.choice(instructors).id if instructors else None,
                prerequisites=[fake.sentence() for _ in range(random.randint(0, 3))],
                learning_outcomes=[fake.sentence() for _ in range(random.randint(3, 5))],
                created_by=program.created_by,
            )
            courses.append(course)

    db.session.add_all(courses)
    db.session.commit()
    return courses


def create_beneficiaries(tenants, users):
    """Create sample beneficiaries."""
    beneficiaries = []

    for tenant in tenants:
        staff = [u for u in users if u.tenant_id == tenant.id and u.role in ["admin", "manager"]]

        for i in range(random.randint(20, 50)):
            beneficiary = Beneficiary(
                tenant_id=tenant.id,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                phone=fake.phone_number(),
                date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=65),
                gender=random.choice(["male", "female", "other"]),
                address=fake.address(),
                city=fake.city(),
                country=fake.country(),
                emergency_contact={
                    "name": fake.name(),
                    "phone": fake.phone_number(),
                    "relationship": random.choice(["parent", "spouse", "sibling", "friend"]),
                },
                status=random.choice(["active", "inactive", "graduated", "dropped"]),
                created_by=random.choice(staff).id if staff else users[0].id,
            )
            beneficiaries.append(beneficiary)

    db.session.add_all(beneficiaries)
    db.session.commit()
    return beneficiaries


def create_enrollments(programs, beneficiaries):
    """Create sample enrollments."""
    enrollments = []

    for program in programs:
        # Get beneficiaries from the same tenant
        tenant_beneficiaries = [b for b in beneficiaries if b.tenant_id == program.tenant_id]

        # Enroll random beneficiaries
        num_enrollments = min(len(tenant_beneficiaries), random.randint(5, 20))
        enrolled = random.sample(tenant_beneficiaries, num_enrollments)

        for beneficiary in enrolled:
            enrollment = Enrollment(
                tenant_id=program.tenant_id,
                program_id=program.id,
                beneficiary_id=beneficiary.id,
                enrollment_date=fake.date_between(
                    start_date=program.start_date - timedelta(days=30), end_date=program.start_date
                ),
                status=random.choice(["enrolled", "active", "completed", "dropped"]),
                completion_date=(
                    fake.date_between(start_date=program.start_date, end_date=program.end_date)
                    if random.random() > 0.5
                    else None
                ),
            )
            enrollments.append(enrollment)

    db.session.add_all(enrollments)
    db.session.commit()
    return enrollments


def create_evaluations(courses, users):
    """Create sample evaluations with questions."""
    evaluations = []

    for course in courses:
        instructors = [u for u in users if u.tenant_id == course.tenant_id and u.has_role("trainer")]

        # Create 1-3 evaluations per course
        for i in range(random.randint(1, 3)):
            evaluation = Evaluation(
                tenant_id=course.tenant_id,
                course_id=course.id,
                name=f"{course.name} - {random.choice(['Midterm', 'Final', 'Quiz'])} {i+1}",
                description=fake.text(max_nb_chars=200),
                evaluation_type=random.choice(["quiz", "exam", "assignment", "project"]),
                max_attempts=random.randint(1, 3),
                time_limit=random.randint(30, 180),
                passing_score=random.randint(60, 80),
                is_adaptive=random.choice([True, False]),
                created_by=random.choice(instructors).id if instructors else course.created_by,
            )
            db.session.add(evaluation)
            db.session.flush()

            # Create questions for each evaluation
            for q in range(random.randint(5, 20)):
                question_type = random.choice(list(QuestionType))

                if question_type == QuestionType.MULTIPLE_CHOICE:
                    options = [fake.sentence() for _ in range(4)]
                    correct_answer = random.choice(options)
                elif question_type == QuestionType.TRUE_FALSE:
                    options = ["True", "False"]
                    correct_answer = random.choice(options)
                else:
                    options = None
                    correct_answer = fake.sentence()

                question = Question(
                    evaluation_id=evaluation.id,
                    question_text=fake.sentence() + "?",
                    question_type=question_type,
                    options=options,
                    correct_answer=correct_answer,
                    points=random.randint(1, 10),
                    difficulty_level=random.randint(1, 5),
                    order_index=q + 1,
                )
                db.session.add(question)

            evaluations.append(evaluation)

    db.session.commit()
    return evaluations


def seed_database(env="local"):
    """Seed the database with sample data."""
    app = create_app()

    with app.app_context():
        print("🌱 Starting database seeding...")

        # Clear existing data if in local environment
        if env == "local":
            print("🗑️  Clearing existing data...")
            db.drop_all()
            db.create_all()

        # Create data
        print("🏢 Creating tenants...")
        tenants = create_tenants()

        print("🔐 Creating roles...")
        roles = create_roles()

        print("👥 Creating users...")
        users = create_users(tenants, roles)

        print("📚 Creating programs...")
        programs = create_programs(tenants, users)

        print("🎓 Creating courses...")
        courses = create_courses(programs, users)

        print("👨‍🎓 Creating beneficiaries...")
        beneficiaries = create_beneficiaries(tenants, users)

        print("📝 Creating enrollments...")
        enrollments = create_enrollments(programs, beneficiaries)

        print("📊 Creating evaluations...")
        evaluations = create_evaluations(courses, users)

        # Print summary
        print("\n✅ Database seeding completed!")
        print(f"   - Tenants: {len(tenants)}")
        print(f"   - Users: {len(users)}")
        print(f"   - Programs: {len(programs)}")
        print(f"   - Courses: {len(courses)}")
        print(f"   - Beneficiaries: {len(beneficiaries)}")
        print(f"   - Enrollments: {len(enrollments)}")
        print(f"   - Evaluations: {len(evaluations)}")
        print(f"\n🔑 Default admin credentials:")
        print(f"   Email: admin@bdc.local")
        print(f"   Password: admin123")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Seed the database")
    parser.add_argument("--env", default="local", help="Environment (local, dev, test)")
    args = parser.parse_args()

    seed_database(args.env)
