from django.db import connection


def fetch_employee_retirement_info():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT a.id, a.assigned_type, a.assigned_date, a.letter_for_issue, a.return_date,
                   a.assigned_condition, a.notes, a.assigned_to, a.equipment_id, a.issue_person_code, 
                   a.issue_person_name, emp.employee_number, emp.user_person_type, emp.employee_name, 
                   emp.date_of_birth, emp.original_date_of_hire, emp.phone_no, emp.email_address, 
                   emp.designation, emp.office, emp.work_location, emp.oic_no, emp.oic_name,
                   -- Calculate months until retirement
                   CASE 
                       WHEN AGE(emp.date_of_birth + INTERVAL '60 years') >= INTERVAL '0 years' THEN 0
                       ELSE (DATE_PART('year', AGE(emp.date_of_birth + INTERVAL '60 years')) * 12 
                             + DATE_PART('month', AGE(emp.date_of_birth + INTERVAL '60 years')))
                   END AS retire_in_month,
                   -- Check if already retired
                   CASE 
                       WHEN AGE(emp.date_of_birth + INTERVAL '60 years') >= INTERVAL '0 years' THEN TRUE
                       ELSE FALSE
                   END AS is_retired
            FROM public.assignments_assignment AS a
            JOIN (
                SELECT employee_number, user_person_type, employee_name, date_of_birth, 
                       original_date_of_hire, phone_no, email_address, designation, office, 
                       work_location, oic_no, oic_name,
                       -- Calculate retirement in months (for those retiring within 1-3 months)
                       CASE 
                           WHEN AGE(date_of_birth + INTERVAL '60 years') >= INTERVAL '0 years' THEN 0
                           ELSE (DATE_PART('year', AGE(date_of_birth + INTERVAL '60 years')) * 12 
                                 + DATE_PART('month', AGE(date_of_birth + INTERVAL '60 years')))
                       END AS retire_in_month
                FROM public.assignees_employee
                WHERE 
                -- Include those retiring within 1-3 months or already retired
                (DATE_PART('year', AGE(date_of_birth + INTERVAL '60 years')) * 12 
                + DATE_PART('month', AGE(date_of_birth + INTERVAL '60 years'))) IN (0, 1, 2, 3)
            ) AS emp
            ON a.assigned_to = emp.employee_number
            WHERE a.assigned_type = 'employee' AND a.return_date IS NULL;
        """)
        
        result = cursor.fetchall()
    return result
