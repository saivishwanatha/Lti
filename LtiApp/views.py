import requests
from django.http import HttpResponse


def retrieve_user_data(api_url, headers, course_id, user_roles):
    user_data_url = f"{api_url}courses/{course_id}/users"
    response = requests.get(user_data_url, headers=headers, params={"enrollment_type[]": user_roles})

    if response.status_code == 200:
        return response.json()
    return []


def retrieve_assignment_data(api_url, headers, course_id):
    assignment_data_url = f"{api_url}courses/{course_id}/assignments"
    response = requests.get(assignment_data_url, headers=headers)

    if response.status_code == 200:
        return response.json()
    return []


def retrieve_submission_status(api_url, headers, course_id, assignment_id, user_id):
    submission_url = f"{api_url}courses/{course_id}/assignments/{assignment_id}/submissions/{user_id}"
    response_submission = requests.get(submission_url, headers=headers)

    if response_submission.status_code == 200:
        submission_data = response_submission.json()
        workflow_state = submission_data.get('workflow_state')

        if workflow_state == 'graded' or workflow_state == 'submitted':
            return 'Submitted'
        else:
            return 'Not Submitted'

    return 'Not Submitted'  # Assume 'Not Submitted' if there's an issue with the API


def index(request):
    api_url = "https://canvas.instructure.com/api/v1/"
    headers = {"Authorization": "Bearer 7~FOVXdSvmi1uz1r4xe2hXB64d59hn7FJGNyJM3Wp7OJn7V1ebnxOuom8mR5FghUZb"}
    course_id = "7989344"
    user_roles = ["student"]

    users_data = retrieve_user_data(api_url, headers, course_id, user_roles)
    assignments_data = retrieve_assignment_data(api_url, headers, course_id)

    if not (users_data and assignments_data):
        return HttpResponse("Data not available", content_type="text/plain")

    result = []

    for user in users_data:
        user_id, user_name = user['id'], user['name']
        assignments = []

        for assignment in assignments_data:
            assignment_name = assignment['name']
            submission_status = retrieve_submission_status(api_url, headers, course_id, assignment['id'], user_id)
            assignments.append({'Assignment Name': assignment_name, 'Submission Status': submission_status})

        result.append({'Student Name': user_name, 'Assignments': assignments})

    output = "List of Assignment Status:\n\n"

    for user in result:
        output += f"Student: {user['Student Name']}\n"
        output += "Assignments:\n"

        for assignment in user.get('Assignments', []):
            assignment_name = assignment.get('Assignment Name', 'Name not available')
            submitted_status = assignment.get('Submission Status', 'Not Submitted')
            output += f"  -> {assignment_name} - {submitted_status}\n"

        output += "\n"

    return HttpResponse(output, content_type="text/plain")
