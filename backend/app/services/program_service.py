"""Service layer for Program operations."""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from app.models.program import Program, ProgramStatus, ProgramType
from app.models.user import User
from app.core.exceptions import NotFoundError, BadRequestError, ForbiddenError
from app.core.logging import logger
from app.services.base import BaseService


class ProgramService(BaseService[Program]):
    """Service for managing programs."""
    
    def __init__(self, db_session: Session):
        """Initialize service."""
        super().__init__(Program, db_session)
    
    def get_all(
        self,
        tenant_id: int,
        user: User,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ProgramStatus] = None,
        program_type: Optional[ProgramType] = None,
        search: Optional[str] = None,
        upcoming_only: bool = False,
        active_only: bool = False
    ) -> List[Program]:
        """
        Get all programs for a tenant with filtering.
        
        Args:
            tenant_id: Tenant ID
            user: Current user
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by program status
            program_type: Filter by program type
            search: Search in title, description, and code
            upcoming_only: Only show upcoming programs
            active_only: Only show active programs
            
        Returns:
            List of programs
        """
        query = self.db.query(Program).filter(
            Program.tenant_id == tenant_id,
            Program.deleted_at.is_(None)
        )
        
        # Apply filters
        if status:
            query = query.filter(Program.status == status)
        
        if program_type:
            query = query.filter(Program.program_type == program_type)
        
        if search:
            search_filter = or_(
                Program.title.ilike(f"%{search}%"),
                Program.description.ilike(f"%{search}%"),
                Program.code.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        if upcoming_only:
            today = datetime.today().date()
            query = query.filter(
                Program.status.in_([ProgramStatus.PUBLISHED, ProgramStatus.ACTIVE]),
                Program.start_date > today
            )
        
        if active_only:
            today = datetime.today().date()
            query = query.filter(
                Program.status == ProgramStatus.ACTIVE,
                Program.start_date <= today,
                Program.end_date >= today
            )
        
        # Order by start date (upcoming first) and title
        query = query.order_by(Program.start_date.desc(), Program.title)
        
        # Apply pagination
        programs = query.offset(skip).limit(limit).all()
        
        logger.info(f"Retrieved {len(programs)} programs for tenant {tenant_id}")
        return programs
    
    def get_by_id(self, tenant_id: int, program_id: int, user: User) -> Program:
        """
        Get a program by ID.
        
        Args:
            tenant_id: Tenant ID
            program_id: Program ID
            user: Current user
            
        Returns:
            Program if found
            
        Raises:
            NotFoundError: If program not found
        """
        program = self.db.query(Program).filter(
            Program.id == program_id,
            Program.tenant_id == tenant_id,
            Program.deleted_at.is_(None)
        ).first()
        
        if not program:
            raise NotFoundError("Program not found")
        
        return program
    
    def get_by_code(self, tenant_id: int, code: str, user: User) -> Program:
        """
        Get a program by code.
        
        Args:
            tenant_id: Tenant ID
            code: Program code
            user: Current user
            
        Returns:
            Program if found
            
        Raises:
            NotFoundError: If program not found
        """
        program = self.db.query(Program).filter(
            Program.code == code,
            Program.tenant_id == tenant_id,
            Program.deleted_at.is_(None)
        ).first()
        
        if not program:
            raise NotFoundError(f"Program with code {code} not found")
        
        return program
    
    def create(self, tenant_id: int, data: Dict[str, Any], user: User) -> Program:
        """
        Create a new program.
        
        Args:
            tenant_id: Tenant ID
            data: Program data
            user: Current user
            
        Returns:
            Created program
            
        Raises:
            BadRequestError: If validation fails
            ForbiddenError: If user doesn't have permission
        """
        # Check permissions
        if user.role not in ['admin', 'manager']:
            raise ForbiddenError("Only admins and managers can create programs")
        
        # Validate dates
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date:
            if start_date > end_date:
                raise BadRequestError("Start date must be before end date")
        
        enrollment_start = data.get('enrollment_start')
        enrollment_end = data.get('enrollment_end')
        
        if enrollment_start and enrollment_end:
            if enrollment_start > enrollment_end:
                raise BadRequestError("Enrollment start must be before enrollment end")
            
            if start_date and enrollment_end > start_date:
                raise BadRequestError("Enrollment must end before program starts")
        
        # Validate capacity
        min_participants = data.get('min_participants', 1)
        max_participants = data.get('max_participants', 50)
        
        if min_participants > max_participants:
            raise BadRequestError("Minimum participants cannot exceed maximum")
        
        # Create program
        program_data = {
            'tenant_id': tenant_id,
            'created_by': user.id,
            **data
        }
        
        program = Program(**program_data)
        
        self.db.add(program)
        self.db.commit()
        self.db.refresh(program)
        
        logger.info(f"Created program {program.code} for tenant {tenant_id}")
        return program
    
    def update(
        self,
        tenant_id: int,
        program_id: int,
        data: Dict[str, Any],
        user: User
    ) -> Program:
        """
        Update a program.
        
        Args:
            tenant_id: Tenant ID
            program_id: Program ID
            data: Update data
            user: Current user
            
        Returns:
            Updated program
            
        Raises:
            NotFoundError: If program not found
            ForbiddenError: If user doesn't have permission
            BadRequestError: If validation fails
        """
        program = self.get_by_id(tenant_id, program_id, user)
        
        # Check permissions
        if user.role not in ['admin', 'manager']:
            raise ForbiddenError("Only admins and managers can update programs")
        
        # Validate dates if provided
        start_date = data.get('start_date', program.start_date)
        end_date = data.get('end_date', program.end_date)
        
        if start_date and end_date:
            if start_date > end_date:
                raise BadRequestError("Start date must be before end date")
        
        # Validate capacity if provided
        min_participants = data.get('min_participants', program.min_participants)
        max_participants = data.get('max_participants', program.max_participants)
        
        if min_participants > max_participants:
            raise BadRequestError("Minimum participants cannot exceed maximum")
        
        # Check if reducing capacity below current enrollment
        if 'max_participants' in data:
            current_enrollment = program.get_enrollment_count()
            if data['max_participants'] < current_enrollment:
                raise BadRequestError(
                    f"Cannot reduce capacity below current enrollment ({current_enrollment})"
                )
        
        # Update fields
        for key, value in data.items():
            if hasattr(program, key) and key not in ['id', 'tenant_id', 'created_at', 'created_by']:
                setattr(program, key, value)
        
        program.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(program)
        
        logger.info(f"Updated program {program.code}")
        return program
    
    def delete(self, tenant_id: int, program_id: int, user: User) -> bool:
        """
        Delete a program (soft delete).
        
        Args:
            tenant_id: Tenant ID
            program_id: Program ID
            user: Current user
            
        Returns:
            True if deleted
            
        Raises:
            NotFoundError: If program not found
            ForbiddenError: If user doesn't have permission
            BadRequestError: If program has active enrollments
        """
        program = self.get_by_id(tenant_id, program_id, user)
        
        # Check permissions
        if user.role != 'admin':
            raise ForbiddenError("Only admins can delete programs")
        
        # Check for active enrollments
        active_enrollments = [
            e for e in program.enrollments 
            if e.status in ['enrolled', 'in_progress']
        ]
        
        if active_enrollments:
            raise BadRequestError(
                f"Cannot delete program with {len(active_enrollments)} active enrollments"
            )
        
        # Soft delete
        program.deleted_at = datetime.utcnow()
        self.db.commit()
        
        logger.info(f"Deleted program {program.code}")
        return True
    
    def update_status(
        self,
        tenant_id: int,
        program_id: int,
        new_status: ProgramStatus,
        user: User
    ) -> Program:
        """
        Update program status.
        
        Args:
            tenant_id: Tenant ID
            program_id: Program ID
            new_status: New status
            user: Current user
            
        Returns:
            Updated program
            
        Raises:
            NotFoundError: If program not found
            ForbiddenError: If user doesn't have permission
            BadRequestError: If status transition invalid
        """
        program = self.get_by_id(tenant_id, program_id, user)
        
        # Check permissions
        if user.role not in ['admin', 'manager']:
            raise ForbiddenError("Only admins and managers can update program status")
        
        try:
            program.update_status(new_status)
            self.db.commit()
            self.db.refresh(program)
            
            logger.info(f"Updated program {program.code} status to {new_status.value}")
            return program
            
        except ValueError as e:
            raise BadRequestError(str(e))
    
    def add_course(
        self,
        tenant_id: int,
        program_id: int,
        course_data: Dict[str, Any],
        user: User
    ) -> Program:
        """
        Add a course to a program.
        
        Args:
            tenant_id: Tenant ID
            program_id: Program ID
            course_data: Course data
            user: Current user
            
        Returns:
            Updated program
            
        Raises:
            NotFoundError: If program not found
            ForbiddenError: If user doesn't have permission
        """
        from app.models.course import Course
        
        program = self.get_by_id(tenant_id, program_id, user)
        
        # Check permissions
        if user.role not in ['admin', 'manager']:
            raise ForbiddenError("Only admins and managers can add courses")
        
        # Create course
        course = Course(
            tenant_id=tenant_id,
            program_id=program.id,
            created_by=user.id,
            **course_data
        )
        
        program.courses.append(course)
        self.db.commit()
        self.db.refresh(program)
        
        logger.info(f"Added course to program {program.code}")
        return program
    
    def get_statistics(self, tenant_id: int, user: User) -> Dict[str, Any]:
        """
        Get program statistics for the tenant.
        
        Args:
            tenant_id: Tenant ID
            user: Current user
            
        Returns:
            Statistics dictionary
        """
        # Check permissions
        if user.role not in ['admin', 'manager']:
            raise ForbiddenError("Only admins and managers can view statistics")
        
        # Total programs by status
        status_counts = self.db.query(
            Program.status,
            func.count(Program.id)
        ).filter(
            Program.tenant_id == tenant_id,
            Program.deleted_at.is_(None)
        ).group_by(Program.status).all()
        
        # Total programs by type
        type_counts = self.db.query(
            Program.program_type,
            func.count(Program.id)
        ).filter(
            Program.tenant_id == tenant_id,
            Program.deleted_at.is_(None)
        ).group_by(Program.program_type).all()
        
        # Get upcoming programs
        today = datetime.today().date()
        upcoming_count = self.db.query(func.count(Program.id)).filter(
            Program.tenant_id == tenant_id,
            Program.deleted_at.is_(None),
            Program.start_date > today,
            Program.status.in_([ProgramStatus.PUBLISHED, ProgramStatus.ACTIVE])
        ).scalar()
        
        # Get active programs
        active_count = self.db.query(func.count(Program.id)).filter(
            Program.tenant_id == tenant_id,
            Program.deleted_at.is_(None),
            Program.status == ProgramStatus.ACTIVE,
            Program.start_date <= today,
            Program.end_date >= today
        ).scalar()
        
        # Calculate total enrollment across all programs
        from app.models.enrollment import Enrollment, EnrollmentStatus
        total_enrollments = self.db.query(func.count(Enrollment.id)).join(
            Program, Enrollment.program_id == Program.id
        ).filter(
            Program.tenant_id == tenant_id,
            Enrollment.status.in_([EnrollmentStatus.ENROLLED, EnrollmentStatus.IN_PROGRESS])
        ).scalar()
        
        return {
            'total_programs': sum(count for _, count in status_counts),
            'status_breakdown': {status.value: count for status, count in status_counts},
            'type_breakdown': {ptype.value: count for ptype, count in type_counts},
            'upcoming_programs': upcoming_count,
            'active_programs': active_count,
            'total_active_enrollments': total_enrollments or 0
        }