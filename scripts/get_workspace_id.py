
import requests
import json
print("please enter clockify API key")
api_key = input()

data = {'x-api-key': api_key}
# r = requests.get('https://api.clockify.me/api/v1/user', headers=data)
# print(r.content)
# quit()

userid="5f65422dd85b7f47a0e857ae"
workspaceid="5e56ce010121f031bdc3a7f2" # ALLFED
# workspaceid="62574afc85712a3bddd78faf" # test

time_entry = {
  "start": "2022-03-12T13:48:14.000Z",
  "billable": "true",
  "description": "ukraine meetings",
  "projectId": "5f2da49c3afc991c82a2546b",
  "end": "2022-03-12T13:50:14.000Z"
}

integrated_model_project_id="602f4800895dec08c3d638ba"
appraisal_project_id="5e56e1317ba4ff284c53a2a9"
KPI_project_id="5e56d8767ba4ff284c539e9d"
time_log_project_id="5e56e1665b92677285acd781"
research_misc_project_id="5e56de580121f031bdc3afac"
outdoor_growing_project_id="5edfcdb1c236b03119337f95"
storms_project_id="60b6534a5b540044b999dc19"
recruitment_project_id="5e56e0c35b92677285acd736"
response_team_project_id="5f2da49c3afc991c82a2546b"
team_meeting_project_id="5e56dfce0121f031bdc3b040"
digital_resilience_project_id="5f50058c3a37e35cbede35ea"
backup_comms_id="5e56dcfd5b92677285acd5b9"
ALLFED_systems_id="5e56df607ba4ff284c53a1e5"
losing_industry_id="5e629ba243f3817e058b8f44"


r = requests.get("https://api.clockify.me/api/v1/workspaces/"+workspaceid+"/user/"+userid+"/time-entries",headers=data)

# r = requests.get("https://api.clockify.me/api/v1/workspaces/"+workspaceid+"/projects",json={"page-size":5000},headers=data)


# r = requests.post("https://api.clockify.me/api/v1/workspaces/"+workspaceid+"/time-entries", json=time_entry, headers=data)
print(r.content)