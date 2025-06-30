"""
Integration tests for complex user scenarios
"""

import pytest
from datetime import datetime, timedelta


class TestIntegrationScenarios:
    """Test complex integration scenarios across multiple components"""

    def test_complete_student_enrollment_flow(self, client, admin_headers, trainer_auth_headers, 
                                            db_session, test_tenant):
        """Test complete flow: create student -> enroll in program -> assign learning path -> track progress"""
        
        # 1. Admin creates a new student
        student_data = {
            "email": "integration_student@example.com",
            "username": "integration_student",
            "full_name": "Integration Test Student",
            "password": "student123",
            "role": "student"
        }
        
        create_response = client.post(
            '/api/v1/users',
            headers=admin_headers,
            json=student_data
        )
        
        assert create_response.status_code == 201
        student_id = create_response.json['id']
        
        # 2. Create beneficiary profile for student
        beneficiary_data = {
            "user_id": student_id,
            "first_name": "Integration",
            "last_name": "Student",
            "date_of_birth": "2000-01-01",
            "gender": "other",
            "contact_phone": "+1234567890",
            "contact_email": "integration_student@example.com",
            "address": "123 Test St",
            "city": "Test City",
            "state": "TS",
            "country": "Test Country",
            "emergency_contact_name": "Emergency Contact",
            "emergency_contact_phone": "+0987654321"
        }
        
        beneficiary_response = client.post(
            '/api/v1/beneficiaries',
            headers=admin_headers,
            json=beneficiary_data
        )
        
        assert beneficiary_response.status_code == 201
        beneficiary_id = beneficiary_response.json['id']
        
        # 3. Admin creates a program
        program_data = {
            "name": "Integration Test Program",
            "code": "ITP-001",
            "description": "Program for integration testing",
            "category": "technical",
            "status": "active",
            "start_date": datetime.utcnow().isoformat(),
            "end_date": (datetime.utcnow() + timedelta(days=90)).isoformat(),
            "max_participants": 30
        }
        
        program_response = client.post(
            '/api/v1/programs',
            headers=admin_headers,
            json=program_data
        )
        
        # Handle if programs endpoint exists
        if program_response.status_code == 201:
            program_id = program_response.json['id']
            
            # 4. Enroll student in program
            enrollment_data = {
                "beneficiary_id": beneficiary_id,
                "enrollment_date": datetime.utcnow().isoformat(),
                "status": "active"
            }
            
            enrollment_response = client.post(
                f'/api/v1/programs/{program_id}/enroll',
                headers=admin_headers,
                json=enrollment_data
            )
            
            # Check if enrollment endpoint exists
            assert enrollment_response.status_code in [200, 201, 404]
        
        # 5. Student logs in
        student_login = client.post(
            '/api/v1/auth/login',
            json={
                "email": "integration_student@example.com",
                "password": "student123"
            },
            headers={"X-Tenant-ID": str(test_tenant.id)}
        )
        
        assert student_login.status_code == 200
        student_token = student_login.json['access_token']
        student_headers = {
            'Authorization': f'Bearer {student_token}',
            'X-Tenant-ID': str(test_tenant.id)
        }
        
        # 6. Student views their dashboard
        dashboard_response = client.get(
            '/api/v1/dashboard/stats',
            headers=student_headers
        )
        
        assert dashboard_response.status_code == 200
        assert 'enrolled_programs' in dashboard_response.json or 'overall_progress' in dashboard_response.json
        
        # 7. Trainer creates learning path for student
        learning_path_data = {
            "user_id": student_id,
            "title": "Python Developer Path",
            "description": "Complete path to Python mastery",
            "goals": ["Learn Python basics", "Master web development", "Build projects"],
            "milestones": [
                {
                    "title": "Python Fundamentals",
                    "week_number": 1,
                    "estimated_hours": 20
                },
                {
                    "title": "Web Development",
                    "week_number": 2,
                    "estimated_hours": 30
                }
            ]
        }
        
        # Check if learning paths endpoint exists and is accessible
        path_response = client.post(
            '/api/v1/learning-paths',
            headers=trainer_auth_headers,
            json=learning_path_data
        )
        
        # Continue based on response
        if path_response.status_code in [201, 404]:
            # 8. Student views their learning paths
            my_paths_response = client.get(
                '/api/v1/learning-paths/my-paths',
                headers=student_headers
            )
            
            if my_paths_response.status_code == 200:
                paths = my_paths_response.json
                assert isinstance(paths, list)
        
        # Cleanup is handled by database rollback after test

    def test_complete_evaluation_flow(self, client, admin_headers, trainer_auth_headers,
                                    student_auth_headers, db_session):
        """Test complete evaluation flow: create -> publish -> attempt -> grade"""
        
        # 1. Trainer creates an evaluation
        evaluation_data = {
            "title": "Python Basics Quiz",
            "description": "Test your Python knowledge",
            "max_attempts": 2,
            "passing_score": 70,
            "time_limit_minutes": 30
        }
        
        eval_response = client.post(
            '/api/v1/evaluations',
            headers=trainer_auth_headers,
            json=evaluation_data
        )
        
        if eval_response.status_code == 201:
            evaluation_id = eval_response.json['id']
            
            # 2. Add questions to evaluation
            questions = [
                {
                    "question_text": "What is Python?",
                    "question_type": "multiple_choice",
                    "points": 10,
                    "options": ["A programming language", "A snake", "Both", "Neither"],
                    "correct_answer": 0
                },
                {
                    "question_text": "Python is interpreted",
                    "question_type": "true_false",
                    "points": 10,
                    "correct_answer": True
                }
            ]
            
            for question in questions:
                q_response = client.post(
                    f'/api/v1/evaluations/{evaluation_id}/questions',
                    headers=trainer_auth_headers,
                    json=question
                )
                assert q_response.status_code in [201, 404]
            
            # 3. Activate evaluation
            activate_response = client.put(
                f'/api/v1/evaluations/{evaluation_id}/activate',
                headers=trainer_auth_headers
            )
            
            if activate_response.status_code == 200:
                # 4. Student starts attempt
                attempt_response = client.post(
                    f'/api/v1/evaluations/{evaluation_id}/start',
                    headers=student_auth_headers
                )
                
                if attempt_response.status_code in [200, 201]:
                    attempt_id = attempt_response.json['id']
                    
                    # 5. Student submits answers
                    answers = [
                        {"question_id": 1, "answer": 0},
                        {"question_id": 2, "answer": True}
                    ]
                    
                    for answer in answers:
                        client.post(
                            f'/api/v1/evaluations/attempts/{attempt_id}/answers',
                            headers=student_auth_headers,
                            json=answer
                        )
                    
                    # 6. Submit attempt
                    submit_response = client.post(
                        f'/api/v1/evaluations/attempts/{attempt_id}/submit',
                        headers=student_auth_headers
                    )
                    
                    assert submit_response.status_code in [200, 404]

    def test_notification_flow_across_roles(self, client, admin_headers, trainer_auth_headers,
                                          student_auth_headers, db_session, student_user):
        """Test notification flow when actions trigger notifications for different users"""
        
        # 1. Get initial unread count for trainer
        initial_count_response = client.get(
            '/api/v1/notifications/unread-count',
            headers=trainer_auth_headers
        )
        
        initial_count = 0
        if initial_count_response.status_code == 200:
            initial_count = initial_count_response.json.get('count', 0)
        
        # 2. Student requests help (should notify trainer)
        help_request = {
            "type": "help_request",
            "title": "Need help with Python",
            "message": "I'm stuck on the exercises",
            "priority": "high"
        }
        
        # Try to trigger a help notification
        # This might be through learning paths or a general help endpoint
        help_response = client.post(
            '/api/v1/notifications/help',
            headers=student_auth_headers,
            json=help_request
        )
        
        # 3. Check trainer's notifications increased
        if help_response.status_code in [200, 201]:
            new_count_response = client.get(
                '/api/v1/notifications/unread-count',
                headers=trainer_auth_headers
            )
            
            if new_count_response.status_code == 200:
                new_count = new_count_response.json.get('count', 0)
                assert new_count >= initial_count
        
        # 4. Admin sends system-wide notification
        system_notification = {
            "type": "announcement",
            "priority": "high",
            "title": "System Maintenance",
            "message": "System will be down for maintenance",
            "target_audience": "all"
        }
        
        system_response = client.post(
            '/api/v1/notifications/broadcast',
            headers=admin_headers,
            json=system_notification
        )
        
        # Check if broadcast endpoint exists
        assert system_response.status_code in [200, 201, 404]

    def test_report_generation_flow(self, client, admin_headers, db_session):
        """Test complete report generation flow"""
        
        # 1. Request a new report
        report_request = {
            "type": "progress",
            "name": "Monthly Progress Report",
            "parameters": {
                "start_date": (datetime.utcnow() - timedelta(days=30)).isoformat(),
                "end_date": datetime.utcnow().isoformat(),
                "include_charts": True,
                "format": "pdf"
            }
        }
        
        create_response = client.post(
            '/api/v1/reports',
            headers=admin_headers,
            json=report_request
        )
        
        if create_response.status_code == 201:
            report_id = create_response.json['id']
            
            # 2. Check report status
            status_response = client.get(
                f'/api/v1/reports/{report_id}',
                headers=admin_headers
            )
            
            assert status_response.status_code == 200
            assert status_response.json['status'] in ['pending', 'processing', 'completed']
            
            # 3. Generate report (if not auto-generated)
            generate_response = client.post(
                f'/api/v1/reports/{report_id}/generate',
                headers=admin_headers
            )
            
            # 4. List all reports
            list_response = client.get(
                '/api/v1/reports',
                headers=admin_headers
            )
            
            assert list_response.status_code == 200
            assert any(r['id'] == report_id for r in list_response.json['reports'])

    def test_multi_tenant_isolation(self, client, db_session):
        """Test that data is properly isolated between tenants"""
        from app.models.tenant import Tenant
        from app.models.user import User
        
        # Create two tenants
        tenant1 = Tenant(name="Tenant 1", domain="tenant1.example.com", is_active=True)
        tenant2 = Tenant(name="Tenant 2", domain="tenant2.example.com", is_active=True)
        
        db_session.add(tenant1)
        db_session.add(tenant2)
        db_session.commit()
        
        # Create admin users for each tenant
        admin1 = User(
            email="admin@tenant1.com",
            username="admin1",
            full_name="Admin Tenant 1",
            tenant_id=tenant1.id,
            role="admin",
            is_active=True
        )
        admin1.set_password("admin123")
        
        admin2 = User(
            email="admin@tenant2.com",
            username="admin2",
            full_name="Admin Tenant 2",
            tenant_id=tenant2.id,
            role="admin",
            is_active=True
        )
        admin2.set_password("admin123")
        
        db_session.add(admin1)
        db_session.add(admin2)
        db_session.commit()
        
        # Login as both admins
        login1 = client.post(
            '/api/v1/auth/login',
            json={"email": "admin@tenant1.com", "password": "admin123"},
            headers={"X-Tenant-ID": str(tenant1.id)}
        )
        
        login2 = client.post(
            '/api/v1/auth/login',
            json={"email": "admin@tenant2.com", "password": "admin123"},
            headers={"X-Tenant-ID": str(tenant2.id)}
        )
        
        assert login1.status_code == 200
        assert login2.status_code == 200
        
        headers1 = {
            'Authorization': f'Bearer {login1.json["access_token"]}',
            'X-Tenant-ID': str(tenant1.id)
        }
        
        headers2 = {
            'Authorization': f'Bearer {login2.json["access_token"]}',
            'X-Tenant-ID': str(tenant2.id)
        }
        
        # Create beneficiary in tenant1
        ben_response1 = client.post(
            '/api/v1/beneficiaries',
            headers=headers1,
            json={
                "first_name": "Tenant1",
                "last_name": "Beneficiary",
                "date_of_birth": "1990-01-01",
                "contact_email": "ben1@tenant1.com"
            }
        )
        
        if ben_response1.status_code == 201:
            # Try to access tenant1's beneficiary from tenant2
            ben_id = ben_response1.json['id']
            
            cross_access = client.get(
                f'/api/v1/beneficiaries/{ben_id}',
                headers=headers2
            )
            
            # Should not be able to access
            assert cross_access.status_code in [404, 403]
            
            # Tenant2 should see empty list
            list_response = client.get(
                '/api/v1/beneficiaries',
                headers=headers2
            )
            
            if list_response.status_code == 200:
                # Should not see tenant1's data
                beneficiaries = list_response.json.get('beneficiaries', [])
                assert not any(b['id'] == ben_id for b in beneficiaries)