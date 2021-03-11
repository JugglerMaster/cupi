### CUPI is a Python module to manage Cisco Unity Connection via the CUPI REST API

### Installation
Clone repository
```bash
git clone https://github.com/bobthebutcher/cupi.git
Cloning into 'cupi'...
remote: Counting objects: 169, done.
remote: Compressing objects: 100% (72/72), done.
remote: Total 169 (delta 95), reused 169 (delta 95), pack-reused 0
Receiving objects: 100% (169/169), 34.65 KiB | 0 bytes/s, done.
Resolving deltas: 100% (95/95), done.
Checking connectivity... done.
```

### Example Usage:
```python
# Update your path
import sys
sys.path.append('./path/CUPI')

# Import CUPI
from cupi.cake import CUPI
```

#### Instantiate connection to Cisco Unity Connection server
`c = CUPI('192.168.200.11', 'username', 'password', diable_warnings=True)`

#### Query server for username
```
print(c.user_query("username"))

{'@total': '1', 'User': {'URI': '/vmrest/users/3867fd84-9eda-4658-b6fa-97e52e0b02e7', 'ObjectId': '3867fd84-9eda-4658-b6fa-97e52e0b02e7', 'FirstName': 'first', 'LastName': 'last', 'Alias': 'username', 'City': '', 'Department': 'Information Technology', 'EmployeeId': '', 'DisplayName': 'first last', 'TimeZone': '20', 'CreationTime': '2015-11-14T03:10:13Z', 
'CosObjectId': '28471e27-6eee-4e17-af9c-305b8966fa32', 'CosURI': '/vmrest/coses/28471e27-6eee-4e17-af9c-305b8966fa32', 'Language': '1033', 'LocationObjectId': '2f95c3e5-c96b-4435-b789-5d294fdb8b50', 'LocationURI': '/vmrest/locations/connectionlocations/2f95c3e5-c96b-4435-b789-5d294fdb8b50', 'ListInDirectory': 'true', 'IsVmEnrolled': 'false', 'MediaSwitchObjectId': '2bb2ed7d-f1d0-4b54-a2aa-37045f9013a2', 'PhoneSystemURI': '/vmrest/phonesystems/2bb2ed7d-f1d0-4b54-a2aa-37045f9013a2', 'CallHandlerObjectId': '42a21be5-c4d3-4378-b672-f88142c51f0b', 'CallhandlerURI': '/vmrest/handlers/callhandlers/42a21be5-c4d3-4378-b672-f88142c51f0b', 'DtmfAccessId': '2367777', 'VoiceNameRequired': 'false', 'PartitionObjectId': '9fcf6aa1-1a57-4e28-a1ce-b9197a2b8cc4', 'PartitionURI': '/vmrest/partitions/9fcf6aa1-1a57-4e28-a1ce-b9197a2b8cc4', 'PhoneNumber': '', 'MwisURI': '/vmrest/users/3867fd84-9eda-4658-b6fa-97e52e0b02e7/mwis', 'NotificationDevicesURI': '/vmrest/users/3867fd84-9eda-4658-b6fa-97e52e0b02e7/notificationdevices', 'MessageHandlersURI': '/vmrest/users/3867fd84-9eda-4658-b6fa-97e52e0b02e7/messagehandlers', 'ExternalServiceAccountsURI': '/vmrest/users/3867fd84-9eda-4658-b6fa-97e52e0b02e7/externalserviceaccounts', 'AlternateExtensionsURI': '/vmrest/users/3867fd84-9eda-4658-b6fa-97e52e0b02e7/alternateextensions', 'PrivateListsURI': '/vmrest/users/3867fd84-9eda-4658-b6fa-97e52e0b02e7/privatelists', 'VideoServiceAccountsURI': '/vmrest/users/3867fd84-9eda-4658-b6fa-97e52e0b02e7/videoserviceaccounts', 'UserWebPasswordURI': '/vmrest/users/3867fd84-9eda-4658-b6fa-97e52e0b02e7/credential/password', 'UserMailboxURI': 
'/vmrest/users/3867fd84-9eda-4658-b6fa-97e52e0b02e7/mailboxattributes', 'MailboxStoreName': 'Unity Messaging Database -1', 'UserVoicePinURI': '/vmrest/users/3867fd84-9eda-4658-b6fa-97e52e0b02e7/credential/pin', 'UserRoleURI': '/vmrest/users/3867fd84-9eda-4658-b6fa-97e52e0b02e7/userroles', 'SmtpProxyAddressesURI': '/vmrest/smtpproxyaddresses?query=(ObjectGlobalUserObjectId%20is%203867fd84-9eda-4658-b6fa-97e52e0b02e7)', 'AlternateNamesURI': '/vmrest/alternatenames?query=(GlobalUserObjectId%20is%203867fd84-9eda-4658-b6fa-97e52e0b02e7)'}}
```

#### Call methods to return information or configure unity
```
c.get_server_info()
{'DatabaseReplication': '0',
 'MacAddress': '',
 'Ipv6Name': '',
 'HostName': 'lab-cuc01',
 'Key': '12d8f9cf-67ce-4bd5-85b6-2f8af4e87f4e',
 'Description': ''}
```

### Configure a Schedule
#### Get the owner location oid
`owner_location_oid = c.get_owner_location_oid()`

#### Add the schedule, default schedule is 8.30am - 5.00pm M-F
```
result = c.add_schedule('Test Schedule 8.30am - 5.00pm M-F', owner_location_oid)
result
('Schedule successfully added',
          '96ce912c-21b8-4589-9b07-b0ad45264865',
          'fb2982b3-ff89-43b7-b541-3a21445a3d50')
```

#### Get Schedules
```
c.get_schedules()
[('Holidays', '31c02cd2-7619-42f7-a1e6-dd1661b6bc20'),
 ('Weekdays', 'e6936d89-8d65-4abc-9df5-d88325910cb0'),
 ('All Hours', '75411de4-f83e-4f85-91fe-9949f443b806'),
 ('Voice Recognition Update Schedule', 'f1261e11-dac3-41a7-abed-7bee9d69a73b'),
 ('Sync Schedule', '3a5a208e-3895-4da3-bbfc-659c860bec3e'),
 ('Test Schedule 8.30am - 5.00pm M-F', 'fb2982b3-ff89-43b7-b541-3a21445a3d50'),
 ('Sync Schedule', 'd0bc824f-dd73-4f2a-9275-b79ade02ab67')]
```
