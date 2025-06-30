# User Roles & Permissions

This guide explains the different user roles in the BDC Platform and their respective permissions. Understanding roles is crucial for effective platform management and ensuring proper access control.

## Table of Contents

- [Overview](#overview)
- [Role Hierarchy](#role-hierarchy)
- [Student/Beneficiary Role](#studentbeneficiary-role)
- [Trainer/Coach Role](#trainercoach-role)
- [Administrator Role](#administrator-role)
- [Permission Matrix](#permission-matrix)
- [Role Management](#role-management)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)

---

## Overview

The BDC Platform uses a role-based access control (RBAC) system with three primary user roles. Each role has specific permissions that determine what features and data users can access.

### Key Principles

- **Least Privilege:** Users receive only the minimum permissions needed for their role
- **Role Inheritance:** Higher-level roles include permissions from lower-level roles
- **Tenant Isolation:** All permissions are scoped to the user's organization (tenant)
- **Audit Trail:** All permission changes are logged for security compliance

### Default Roles

1. **Student/Beneficiary** - Program participants
2. **Trainer/Coach** - Program instructors and mentors
3. **Administrator** - System and organization managers

---

## Role Hierarchy

```
Administrator (Highest Level)
    ├── Full system access
    ├── User management
    ├── System configuration
    └── All trainer permissions
        │
        Trainer/Coach (Middle Level)
        ├── Student management
        ├── Program creation
        ├── Evaluation management
        └── All student permissions
            │
            Student/Beneficiary (Base Level)
            ├── Program enrollment
            ├── Assessment participation
            └── Personal progress tracking
```

---

## Student/Beneficiary Role

Students are the primary beneficiaries of training programs. They participate in learning activities and track their progress.

### Core Permissions

**✅ Allowed Actions:**
- View and enroll in available programs
- Take assessments and evaluations
- Track personal learning progress
- View personal dashboard and statistics
- Download earned certificates
- Communicate with assigned coaches
- Update personal profile information
- View learning materials and resources

**❌ Restricted Actions:**
- Cannot create or modify programs
- Cannot access other students' data
- Cannot perform administrative functions
- Cannot assign coaches or manage users
- Cannot view system-wide statistics

### Dashboard Features

**Student Dashboard Includes:**
- Personal progress overview
- Active program enrollment status
- Upcoming assessment deadlines
- Recent achievements and certificates
- Coach messages and feedback
- Learning goal tracking

### Navigation Menu

**Available Sections:**
- 🏠 **Dashboard** - Personal overview
- 📚 **My Programs** - Enrolled programs
- 📊 **Assessments** - Available and completed evaluations
- 🏆 **Achievements** - Certificates and milestones
- 💬 **Messages** - Coach communication
- ⚙️ **Profile** - Personal settings

---

## Trainer/Coach Role

Trainers manage students, create programs, and oversee educational activities. They have elevated permissions to support their teaching responsibilities.

### Core Permissions

**✅ Allowed Actions:**
- All student permissions (inherited)
- Manage assigned students
- Create and modify training programs
- Design and schedule evaluations
- Add coach notes and feedback
- View student progress and analytics
- Generate student performance reports
- Assign and remove students from programs
- Configure program prerequisites
- Upload and manage learning materials

**❌ Restricted Actions:**
- Cannot manage other trainers or administrators
- Cannot access system configuration
- Cannot view financial or billing information
- Cannot delete system-critical data
- Limited to assigned students and programs

### Advanced Features

**Program Management:**
- Create custom learning paths
- Set program prerequisites and requirements
- Configure evaluation criteria
- Manage program schedules and deadlines
- Track program completion rates

**Student Oversight:**
- Monitor individual student progress
- Identify at-risk students
- Provide personalized feedback
- Schedule one-on-one sessions
- Generate progress reports

### Dashboard Features

**Trainer Dashboard Includes:**
- Student performance overview
- Program management tools
- Evaluation scheduling interface
- Recent student activities
- Performance analytics
- Quick action buttons

### Navigation Menu

**Available Sections:**
- 🏠 **Dashboard** - Overview and analytics
- 👥 **My Students** - Student management
- 📚 **Programs** - Program creation and management
- 📊 **Evaluations** - Assessment tools
- 💼 **Coach Notes** - Student feedback system
- 📈 **Reports** - Student analytics
- ⚙️ **Settings** - Trainer preferences

---

## Administrator Role

Administrators have full system access and manage the entire organization's BDC platform instance.

### Core Permissions

**✅ Allowed Actions:**
- All trainer and student permissions (inherited)
- Manage all users and roles
- System configuration and settings
- Organization-wide reporting and analytics
- User account creation and deletion
- Security settings management
- Audit log access
- Platform customization
- Integration management
- Backup and data management

**🔧 System Administration:**
- Configure authentication settings
- Manage API access and rate limits
- Set up automated notifications
- Configure data retention policies
- Manage platform integrations
- Monitor system performance

### Advanced Administrative Functions

**User Management:**
- Create and manage user accounts
- Assign and modify user roles
- Reset passwords and unlock accounts
- Manage user permissions
- Bulk user operations
- User activity monitoring

**Organization Management:**
- Configure organizational settings
- Manage multiple programs simultaneously
- Set up departmental structures
- Configure custom fields and workflows
- Manage platform branding and customization

**Analytics and Reporting:**
- Access comprehensive platform analytics
- Generate organization-wide reports
- Monitor system usage and performance
- Track learning outcomes and ROI
- Export data for external analysis

### Dashboard Features

**Administrator Dashboard Includes:**
- Organization-wide statistics
- System health monitoring
- User activity overview
- Platform usage analytics
- Security alerts and notifications
- Quick administrative actions

### Navigation Menu

**Available Sections:**
- 🏠 **Dashboard** - System overview
- 👥 **Users** - User management
- 🏢 **Organization** - Org settings
- 📚 **Programs** - All programs
- 📊 **Analytics** - Platform analytics
- 🔐 **Security** - Security settings
- ⚙️ **System** - Platform configuration
- 📋 **Audit Logs** - Security auditing

---

## Permission Matrix

| Feature | Student | Trainer | Admin |
|---------|---------|---------|-------|
| **Dashboard Access** | ✅ Personal | ✅ Students | ✅ System-wide |
| **Program Enrollment** | ✅ Self only | ✅ Manage students | ✅ All users |
| **Program Creation** | ❌ | ✅ Own programs | ✅ All programs |
| **User Management** | ❌ | ❌ | ✅ Full access |
| **Take Assessments** | ✅ | ✅ | ✅ |
| **Create Assessments** | ❌ | ✅ | ✅ |
| **View Analytics** | ✅ Personal | ✅ Students | ✅ System-wide |
| **Coach Notes** | ✅ View own | ✅ Create/Edit | ✅ All access |
| **System Settings** | ❌ | ❌ | ✅ Full access |
| **Security Logs** | ❌ | ❌ | ✅ Full access |
| **API Access** | ✅ Limited | ✅ Extended | ✅ Full access |
| **Data Export** | ✅ Personal | ✅ Students | ✅ All data |

---

## Role Management

### Assigning Roles

**For Administrators:**

1. **Navigate to User Management**
   - Go to **Users** section in admin panel
   - Find the user account
   - Click "Edit" or "Manage Roles"

2. **Modify Role Assignment**
   - Select new role from dropdown
   - Confirm role change
   - Notify user of permission changes

3. **Bulk Role Operations**
   - Select multiple users
   - Choose "Bulk Actions" → "Change Role"
   - Confirm mass role change

### Role Change Process

1. **Request Submission**
   - User or supervisor submits role change request
   - Include justification and new responsibilities

2. **Administrative Review**
   - Administrator reviews request
   - Verifies business justification
   - Checks with user's supervisor

3. **Implementation**
   - Role change applied to user account
   - User notified of new permissions
   - Training provided if necessary

4. **Monitoring**
   - Monitor user activity in new role
   - Ensure appropriate use of permissions
   - Review role effectiveness after 30 days

### Best Practices

**Role Assignment Guidelines:**
- Assign minimum necessary permissions
- Review roles quarterly
- Document role change justifications
- Provide role-specific training
- Monitor for privilege escalation

**Security Considerations:**
- Implement approval workflows for role changes
- Require justification for administrative access
- Regular access reviews and audits
- Separation of duties for critical functions

---

## Security Considerations

### Access Control Principles

**Authentication Requirements:**
- Strong password policies enforced
- Multi-factor authentication for administrators
- Session timeout policies
- Failed login attempt monitoring

**Authorization Controls:**
- Role-based permissions strictly enforced
- Regular permission audits
- Principle of least privilege
- Tenant-based data isolation

### Audit and Monitoring

**Activity Logging:**
- All user actions logged with timestamps
- Permission changes tracked
- Failed access attempts recorded
- Suspicious activity alerts

**Regular Reviews:**
- Monthly access reviews for trainers
- Quarterly comprehensive audits
- Annual role effectiveness assessment
- Continuous security monitoring

### Compliance

**Data Protection:**
- User data access limited by role
- Personal information protection
- Student privacy safeguards
- GDPR/FERPA compliance measures

---

## Troubleshooting

### Common Permission Issues

**"Access Denied" Errors:**

1. **Check User Role**
   - Verify current role assignment
   - Confirm role includes required permissions
   - Check for recent role changes

2. **Verify Session Status**
   - Ensure user is properly logged in
   - Check for expired authentication
   - Verify multi-factor authentication

3. **Contact Administrator**
   - Report specific error messages
   - Provide screenshot of issue
   - Include attempted action details

**Missing Features:**

1. **Role Verification**
   - Confirm feature is available for user role
   - Check permission matrix above
   - Verify organizational feature settings

2. **Browser Issues**
   - Clear browser cache and cookies
   - Disable browser extensions
   - Try different browser

3. **Platform Updates**
   - Check for recent platform updates
   - Verify feature availability
   - Contact support for assistance

### Getting Help

**For Permission Questions:**
- Contact your administrator
- Reference this permissions guide
- Submit support ticket with role/permission details

**For Technical Issues:**
- Try browser troubleshooting first
- Contact technical support
- Provide specific error messages

**For Role Change Requests:**
- Contact your supervisor or administrator
- Provide business justification
- Allow time for approval process

---

## Related Documentation

- [Getting Started Guide](./01-getting-started.md) - Platform basics
- [Admin Functions](./07-admin-functions.md) - Administrative features
- [Student Management](./03-student-management.md) - Managing students
- [Program Management](./04-program-management.md) - Program creation

---

*Understanding roles and permissions ensures secure and effective use of the BDC Platform. Contact your administrator if you have questions about your specific permissions.*

*Last updated: June 27, 2025 | Version 1.0*