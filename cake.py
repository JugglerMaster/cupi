"""
Class to interface with cisco unity connection cupi api.
Author: Brad Searle
Version: 0.4.4
Dependencies:
- requests: http://docs.python-requests.org/en/latest/
CUPI api reference on password resets https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/connection/REST-API/CUPI_API/b_CUPI-API/b_CUPI-API_chapter_011110.pdf
CUPI current docs https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/connection/REST-API/CUPI_API/b_CUPI-API/b_CUPI-API_chapter_011110.html#reference_38E38BB12CB64112AD637A337837CF55
"""

import requests


class CUPI(object):
    status = ""
    """
    Class for configuring Cisco Unity

    example usage:
    >>> from cupi.cake import CUPI
    >>> c = CUPI('192.168.200.11', 'username', 'password')
    >>> c.get_owner_location_oid()
    >>> '89443b75-0547-4008-8245-39c3abeaed31'
    """

    def __init__(self, cuc, username, password, verify=False, disable_warnings=False, timeout=20):
        """
        Sets up the connection to Cisco Unity Connection

        :param cuc: Unity connection IP Address
        :param username: User with privilege to access rest api
        :param password: Users password
        :param verify: Verify SSL certificate
        :param disable_warnings: Disable console warnings if ssl cert invalid
        :param timeout: Timeout for request response
        """

        self.url_base = 'https://{0}/vmrest'.format(cuc)
        self.cuc = requests.session()
        self.cuc.auth = (username, password)
        self.cuc.verify = verify  # http://docs.python-requests.org/en/latest/user/advanced/#ssl-cert-verification
        self.disable_warnings = disable_warnings
        self.timeout = timeout
        self.cuc.headers.update({
            'Accept': 'application/json',
            'Connection': 'keep_alive',
            'Content-type': 'application/json',
        })
        self.keep_alive = False
        if self.disable_warnings:
            requests.packages.urllib3.disable_warnings()
        
    def get_server_info(self, online_test=False):
        """
        Get information relating to the server configuration
        :param online_test: return 200 if API online
        :return: dictionary of values or 200
        """
        url = '{0}/cluster'.format(self.url_base)
        resp = self.cuc.get(url, timeout=self.timeout)
        if online_test:
            return True
        else:
            CUPI.status = resp.json()['Server']
            print(CUPI.status)
            return False

    def user_query(self, username):
        """
        Get the user based on just the alias
        :return: An xml list of data for the user e.g. DtmfAccessId, Alias, FirstName, LastName, DisplayName
        """
        #vmrest/users?query=(alias%20is%20username)
        url = '{0}/users?query=(alias is {1})'.format(self.url_base, username)
        resp = self.cuc.get(url, timeout=self.timeout)
        return resp.json()

    def get_oid(self, username):
        url = '{0}/users?query=(alias is {1})'.format(self.url_base, username)
        resp = self.cuc.get(url, timeout=self.timeout)
        return resp.json()["User"]['ObjectId']
    def ext_query(self, DtmfAccessId):
        """
        Check if extension exists
        :return: An xml list of data for the user e.g. DtmfAccessId, Alias, FirstName, LastName, DisplayName
        """
        #vmrest/users?query=(alias%20is%20username)
        url = '{0}/users?query=(DtmfAccessId is {1})'.format(self.url_base, DtmfAccessId)
        resp = self.cuc.get(url, timeout=self.timeout)
        return resp.json()
    #def delete_ext(self, ext):

    def unlock_pin_username(self, username):
        results = CUPI.user_query(self, username)
        user_oid = results["User"]['ObjectId']
        url = '{0}/users/{1}/credential/pin'.format(self.url_base, user_oid)
        body = {"HackCount":"0", "TimeHacked":""}

        resp = self.cuc.put(url, json=body, timeout=self.timeout)
        if resp.status_code != 204:
            CUPI.status = 'Could not unlock VM PIN: {0} {1} {2}'.format(resp.status_code, resp.reason, resp.text)
            print(CUPI.status)
            return False
        else:
            CUPI.status = 'User VM successfully unlocked', username
            print(CUPI.status)
            return True
    def set_pin_username(self, pin, username):
        self.cuc.headers.update({
            'Accept': 'application/json',
            'Content-type': 'application/json',
            'Connection': 'keep-alive',
        })
        results = CUPI.user_query(self, username)
        user_oid = results["User"]['ObjectId']
        #print(results)
        #print("ObjectID:")
        #print(user_oid) 
        url = '{0}/users/{1}/credential/pin'.format(self.url_base, user_oid)
        body = {'CredMustChange':'true', "Credentials": pin}
        #print(url)
        print(body)

        resp = self.cuc.put(url, json=body, timeout=self.timeout)
        print(resp)
        if resp.status_code != 204:
            CUPI.status = 'Could not update VM PIN: {0} {1} {2}'.format(resp.status_code, resp.reason, resp.text)
            print(CUPI.status)
            return False
        else:
            CUPI.status = 'Successfully set password and set to must change', username
            print(CUPI.status)
            return True
            
    def get_license_info(self, mini=True):
        """
        Get the CUC server licensing information
        :param mini: Returns a list of tuples containing licensing information
        :return: A list or dictionary of licensing information
        """
        url = '{0}/licensestatuscounts'.format(self.url_base)
        resp = self.cuc.get(url, timeout=self.timeout)

        if mini:
            return [(i['featureName'], i['TagName'], i['description'], i['Count'])
                    for i in resp.json()['LicenseStatusCount']]
        else:
            return resp.json()

    def get_languages(self):
        """
        Get a dictionary of languages
        :return: Dictionary of languages
        """
        url = '{0}/languagemap'.format(self.url_base)
        resp = self.cuc.get(url, timeout=self.timeout)
        return resp.json()

    def get_owner_location_oid(self):
        """
        Get the owner location oid. This is needed for creating schedules
        :return: owner location oid as a string
        """
        url = '{0}/locations/connectionlocations'.format(self.url_base)
        resp = self.cuc.get(url, timeout=self.timeout)
        return resp.json()['ConnectionLocation']['ObjectId']

    def get_schedule_sets(self, mini=True):
        """
        Get Schedule Sets
        :param mini: return minimal list if True else return full json response
        :return: a list of tuples of schedule sets
        """
        url = '{0}/schedulesets'.format(self.url_base)
        resp = self.cuc.get(url, timeout=self.timeout)

        if mini:
            return [(i['DisplayName'], i['ObjectId']) for i in resp.json()['ScheduleSet']]
        else:
            return resp.json()

    def get_schedules(self, mini=True):
        """
        Get Schedules
        :param mini: return minimal list if True else return full json response
        :return: a list of tuples of schedules or a dictionary of schedules
        """
        url = '{0}/schedules'.format(self.url_base)
        resp = self.cuc.get(url, timeout=self.timeout)

        if mini:
            return [(i['DisplayName'], i['ObjectId']) for i in resp.json()['Schedule']]
        else:
            return resp.json()

    def get_schedule(self, schedule_oid):
        """
        Get a single schedule
        :param schedule_oid: the oid of the schedule to get info for
        :return: a dictionary of schedule info
        """

        url = '{0}/schedules/{1}'.format(self.url_base, schedule_oid)
        resp = self.cuc.get(url, timeout=self.timeout)
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 404:
            return 'Schedule not found'
        else:
            return 'Unknown result: {0} {1} {2}'.format(resp.status_code, resp.reason, resp.text)

    def add_schedule(self,
                     display_name,
                     owner_location_oid,
                     is_holiday='false',
                     start_time='510',
                     end_time='1020',
                     is_active_monday='true',
                     is_active_tuesday='true',
                     is_active_wednesday='true',
                     is_active_thursday='true',
                     is_active_friday='true',
                     is_active_saturday='false',
                     is_active_sunday='false'):
        """
        To add a schedule there are 4 steps
        1) Add a schedule set
        2) Add a schedule
        3) Map the schedule to the scheduleset with a schedule set map
        4) Add a schedule detail to the schedule

        Default schedule times are Monday - Friday 8.30am - 5.00pm
        Start/Finish Times are calculated as number of minutes past midnight
        IE: 8:30am is 510 minutes past midnight
        Minute portion must be in 5 minute blocks
        IE: 8:31am = 511 == WAH WAH

        :param display_name: Schedule display name
        :param owner_location_oid: Get this oid with the get_owner_location_oid method
        :param is_holiday: Is this schedule a holiday schedule true/false
        :param start_time: Schedule start time
        :param end_time: Schedule end time
        :param is_active_monday: Schedule active Monday true/false
        :param is_active_tuesday: Schedule active Tuesday true/false
        :param is_active_wednesday: Schedule active Wednesday true/false
        :param is_active_thursday: Schedule active Thursday true/false
        :param is_active_friday: Schedule active Friday true/false
        :param is_active_saturday: Schedule active Saturday true/false
        :param is_active_sunday: Schedule active Sunday true/false
        :return: Result of adding the schedule, & schedule_set_oid, schedule_oid if successful
        """

        # 1) Add a schedule set
        url = '{0}/schedulesets'.format(self.url_base)
        body = {
            'DisplayName': display_name,
            'OwnerLocationObjectId': owner_location_oid,
        }

        resp = self.cuc.post(url, json=body, timeout=self.timeout)
        schedule_set_oid = resp.text.split('/')[-1]

        if resp.status_code != 201:
            return 'Could not add schedule set: {0} {1}'.format(resp.status_code, resp.reason, resp.text)

        # 2) Add a schedule
        else:
            url = '{0}/schedules'.format(self.url_base)
            body = {
                'DisplayName': display_name,
                'OwnerLocationObjectId': owner_location_oid,
                'IsHoliday': is_holiday
            }

            resp = self.cuc.post(url, json=body, timeout=self.timeout)
            schedule_oid = resp.text.split('/')[-1]

            if resp.status_code != 201:
                return 'Could not add schedule: {0} {1} {2}'.format(resp.status_code, resp.reason, resp.text)

            # 3) Map the schedule to the schedule set with a schedule set map
            else:
                url = '{0}/schedulesets/{1}/schedulesetmembers'.format(self.url_base, schedule_set_oid)
                body = {
                    'ScheduleSetObjectId': schedule_set_oid,
                    'ScheduleObjectId': schedule_oid,
                    'Exclude': 'false'  # Must be false for non-holiday schedule
                }

                resp = self.cuc.post(url, json=body, timeout=self.timeout)

                if resp.status_code != 201:
                    return 'Could not map schedule to schedule set: {0} {1} {2}'.format(
                            resp.status_code, resp.reason, resp.text)

                # 4) Add a schedule detail to the schedule
                else:
                    url = '{0}/schedules/{1}/scheduledetails'.format(self.url_base, schedule_oid)
                    body = {
                        'Subject': display_name,
                        'StartTime': start_time,
                        'EndTime': end_time,
                        'IsActiveMonday': is_active_monday,
                        'IsActiveTuesday': is_active_tuesday,
                        'IsActiveWednesday': is_active_wednesday,
                        'IsActiveThursday': is_active_thursday,
                        'IsActiveFriday': is_active_friday,
                        'IsActiveSaturday': is_active_saturday,
                        'IsActiveSunday': is_active_sunday,
                    }

                    resp = self.cuc.post(url, json=body, timeout=self.timeout)

                    if resp.status_code != 201:
                        return 'Could not add schedule detail: {0} {1} {2}'.format(
                                resp.status_code, resp.reason, resp.text)

                    else:
                        return 'Schedule successfully added', schedule_set_oid, schedule_oid

    def update_schedule_holiday(self, schedule_set_oid, holiday_oid):
        """
        Update a schedules holiday schedule
        :param schedule_set_oid: Schedule set OID
        :param holiday_oid: OID of the holiday schedule to assign
        :return: Result as a string
        """
        url = '{0}/schedulesets/{1}/schedulesetmembers'.format(self.url_base, schedule_set_oid)
        body = {
            'ScheduleSetObjectId': schedule_set_oid,
            'ScheduleObjectId': holiday_oid,
            'Exclude': 'true'  # Must be true for holiday schedule
        }

        resp = self.cuc.post(url, json=body, timeout=self.timeout)

        if resp.status_code == 201:
            return 'Schedules holiday schedule successfully updated'
        else:
            return 'Could not map holiday to schedule: {0} {1} {2}'.format(
                    resp.status_code, resp.reason, resp.text)

    def delete_schedule_set(self, schedule_set_oid):
        """
        Delete a schedule set
        :param schedule_set_oid: OID of the schedule set to delete
        :return: Result as a string
        """

        url = '{0}/schedulesets/{1}'.format(self.url_base, schedule_set_oid)

        resp = self.cuc.delete(url, timeout=self.timeout)
        if resp.status_code == 204:
            return 'Schedule set deleted'
        elif resp.status_code == 404:
            return 'Schedule set not found'
        else:
            return 'Unknown result: {0} {1} {2}'.format(resp.status_code, resp.reason, resp.text)

    def delete_schedule(self, schedule_oid):
        """
        Delete a schedule
        :param schedule_oid: OID of the schedule to delete
        :return: Result as a string
        """

        url = '{0}/schedules/{1}'.format(self.url_base, schedule_oid)
        resp = self.cuc.delete(url, timeout=self.timeout)

        if resp.status_code == 204:
            return 'Schedule deleted'
        elif resp.status_code == 404:
            return 'Schedule not found'
        else:
            return 'Unknown result: {0} {1} {2}'.format(resp.status_code, resp.reason, resp.text)

    def get_user_call_handler_oid(self, user_oid):
        """
        Get the oid of a call handler assigned to a user
        :param user_oid: oid of the user to get the call handler oid
        :return: users call handler oid
        """

        url = '{0}/users/{1}'.format(self.url_base, user_oid)
        resp = self.cuc.get(url, timeout=self.timeout)

        if resp.status_code == 200:
            return resp.json()['CallHandlerObjectId']
        elif resp.status_code == 404:
            return 'User not found'
        else:
            return 'Unknown result: {0} {1} {2}'.format(resp.status_code, resp.reason, resp.text)

    def get_users(self, mini=True):
        """
        Get all users
        :param mini: if True returns a tuple of user information
        :return: A tuple or list of user dictionaries of user information
        """

        url = '{0}/users'.format(self.url_base)
        resp = self.cuc.get(url, timeout=self.timeout)

        if mini:
            return [(i['DisplayName'], i['DtmfAccessId'], i['ObjectId'], i['TimeZone']) for i in resp.json()['User']]
        else:
            return resp.json()

    def get_user(self, user_oid):
        """
        Get user info
        :param user_oid: OID of the user
        :return: A dictionary of user parameters
        """

        url = '{0}/users/{1}'.format(self.url_base, user_oid)
        resp = self.cuc.get(url, timeout=self.timeout)

        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 404:
            
            return 'User not found'
        else:
            return 'Unknown result: {0} {1} {2}'.format(resp.status_code, resp.reason, resp.text)

    def get_user_pin_settings(self, user_oid):
        """
        Get a users pin settings
        :param user_oid:
        :return:
        """

        url = '{0}/users/{1}/credential/pin'.format(self.url_base, user_oid)
        resp = self.cuc.get(url, timeout=self.timeout)

        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 404:
            return 'User not found'
        else:
            return 'Unknown result: {0} {1} {2}'.format(resp.status_code, resp.reason, resp.text)

    def get_user_password_settings(self, user_oid):
        """
        Get a users password settings
        :param user_oid:
        :return:
        """

        url = '{0}/users/{1}/credential/password'.format(self.url_base, user_oid)
        resp = self.cuc.get(url, timeout=self.timeout)

        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 404:
            return 'User not found'
        else:
            return 'Unknown result: {0} {1} {2}'.format(resp.status_code, resp.reason, resp.text)

    def get_user_templates(self):
        """
        Get user templates, used when adding users
        :return: a list of tuples of user template alias's and oid's
        """

        url = '{0}/usertemplates'.format(self.url_base)
        resp = self.cuc.get(url, timeout=self.timeout).json()

        if resp['@total'] == '1':
            # if there is only one result the response will not be in a list
            return [(resp['UserTemplate']['Alias'], resp['UserTemplate']['ObjectId'])]
        else:
            return [(i['Alias'], i['ObjectId']) for i in resp['UserTemplate']]
    def update_email(self, username, email):
        """
        update user's email
        """
        results = CUPI.user_query(self, username)
        user_oid = results["User"]['ObjectId']
        #/vmrest/users/{objectid}
        #<DisplayName>johnd</DisplayName>
        url = '{0}/users/{1}'.format(self.url_base, user_oid)
        body = {
           
            'EmailAddress': email,
        }
        resp = self.cuc.post(url, json=body, timeout=self.timeout)
    def add_user(self,
                 display_name,
                 dtmf_access_id,
                 first_name,
                 last_name,
                 user_template,
                 #timezone,
                 emailAddress,
                 is_vm_enrolled='false',
                 #country='US',
                # use_default_timezone='false',
                 cred_must_change='true',
                 IsVmEnrolled='true'):
        """
        Add a user
        :param display_name:
        :param dtmf_access_id: (extension)
        :param first_name:
        :param last_name:
        :param user_template:
        :param emailAddress:
        :param is_vm_enrolled: (default=false)
        :param cred_must_change:
        :param IsVmEnrolled: (default=true)
        :return: Result & user_oid if successful

        example usage:
                                 dtmf_access_id             last_name                       timezone
                      display_name     V      first_name        V         user_template         V
        >>> c.add_user('Test User', '77777', 'First Name', 'Last Name', 'Test User Template', '255')
        >>> 'e16922d4-aabf-4dec-9e83-9abaa64dfa02'
        """
        url = '{0}/users?templateAlias={1}'.format(self.url_base, user_template)
        coses = self.query_class_of_service()['Cos'][3]['ObjectId']
        print("Email: " + emailAddress)
        body = {
            'Alias': display_name,
            'DisplayName': display_name,
            'DtmfAccessId': dtmf_access_id,
            'FirstName': first_name,
            'LastName': last_name,
            'IsVmEnrolled': is_vm_enrolled,
            #'Country': country,
            #'UseDefaultTimeZone': use_default_timezone,
            #'TimeZone': timezone,
            'EmailAddress': emailAddress,
            'IsVmEnrolled': IsVmEnrolled,
            'CosObjectId': coses
        }

        resp = self.cuc.post(url, json=body, timeout=self.timeout)
        user_oid = resp.text.split('/')[-1]

        if resp.status_code != 201:
            return 'Could not add user: {0} {1} {2}'.format(resp.status_code, resp.reason, resp.text)
        elif cred_must_change == 'false':

            url = '{0}/users/{1}/credential/pin'.format(self.url_base, user_oid)
            body = {'CredMustChange': 'false'}

            resp = self.cuc.put(url, json=body, timeout=self.timeout)
            if resp.status_code != 204:
                return 'Could not update VM PIN property: {0} {1} {2}'.format(resp.status_code, resp.reason, resp.text)
            else:
                return 'User successfully added', user_oid
        else:
            return 'User successfully added', user_oid
    def query_um_template(self):
        #https://usiptpuc01.hbfuller.com/vmrest/externalservices
        url = '{0}/externalservices'.format(self.url_base)
        resp = self.cuc.get(url, timeout=self.timeout)
        print(resp.json())
        return resp.json()
    def query_class_of_service(self):
        url = '{0}/coses'.format(self.url_base)
        resp = self.cuc.get(url, timeout=self.timeout)
        return resp.json()
    def set_class_of_service(self, username):
        coses = self.query_class_of_service()['Cos'][3]
        results = CUPI.user_query(self, username)
        user_oid = results["User"]['ObjectId']
        print(coses)
        url = '{0}/users/{1}'.format(self.url_base, user_oid)
        body = {"CosObjectId":coses['ObjectId']}
        #'Post url https://<connection-server>/vmrest/users/<user-objectid>'
        print(url)
        print(body)
        resp = self.cuc.put(url, json=body, timeout=self.timeout)
        if resp.status_code == 204:
            CUPI.status = 'Changed Class of Service to Single in box: ' + username
            print(CUPI.status)
            return True
        else:
            CUPI.status = 'Unknown result: {0} {1} {2}'.format(resp.status_code, resp.reason, resp.text)
            print(CUPI.status)
            return False
    def get_user_templates(self):
        #https://<connection-server>/vmrest/usertemplates
        #look for <Alias>
        url = '{0}/usertemplates'.format(self.url_base)
        resp = self.cuc.get(url, timeout=self.timeout)
        return resp.json()
    def add_unified_messaging(self, username):
        """ test"""
        results = CUPI.user_query(self, username)
        user_oid = results["User"]['ObjectId']
        
        results = CUPI.query_um_template(self)
        #print(results)
        um_account = results['ExternalService']['ObjectId']
        #user_oid = results["User"]['ObjectId']
        url = '{0}/users/{1}/externalserviceaccounts'.format(self.url_base, user_oid, um_account)
        body = {"ExternalServiceObjectId": um_account, "SubscriberObjectId": user_oid, 'EnableMeetingCapability': 'false', 'IsPrimaryMeetingService': 'false', 'UserURI': "/vmrest/users/" + user_oid, "LoginType": "0", "UserPassword": "", "EmailAddressUseCorp": "true", "EnableCalendarCapability":"false", "EnableMailboxSynchCapability":"true", "EnablTtsOfEmailCapability":"false"}
        #'Post url https://<connection-server>/vmrest/users/<user-objectid>/externalserviceaccounts'
        print(url)
        print(body)
        resp = self.cuc.post(url, json=body, timeout=self.timeout)

        if resp.status_code == 201:
            CUPI.status = 'Unified Messaging Account Added to ' + username
            print(CUPI.status)
            return True
        else:
            CUPI.status = 'Unknown result: {0} {1} {2}'.format(resp.status_code, resp.reason, resp.text)
            print(CUPI.status)
            return False

    def update_user_schedule(self, user_call_handler_oid, schedule_set_oid):
        """
        Note: To update the ScheduleSetObjectId the users call handler OID is needed.
              Get this with the get_user_call_handler_oid method
        :param user_call_handler_oid:
        :param schedule_set_oid:
        :return:
        """
        url = '{0}/handlers/callhandlers/{1}'.format(self.url_base, user_call_handler_oid)
        body = {'ScheduleSetObjectId': schedule_set_oid}

        resp = self.cuc.put(url, json=body, timeout=self.timeout)

        if resp.status_code == 204:
            return 'User schedule updated'
        else:
            return 'Unknown result: {0} {1} {2}'.format(resp.status_code, resp.reason, resp.text)

    def change_user_vm_pin(self, dtmf_access_id, new_pin):
        """

        :param dtmf_access_id:
        :param new_pin:
        :return:
        """

        # find user oid by searching with the directory number
        url = '{0}/users?query=(DtmfAccessId%20is%20{1})'.format(self.url_base, dtmf_access_id)
        resp = self.cuc.get(url, timeout=self.timeout)

        if resp.status_code != 200:
            CUPI.status = 'Something went wrong: {0} {1} {2}'.format(resp.status_code, resp.reason, resp.text)
            print(CUPI.status)
            return False
        elif resp.json()['@total'] == '1':
            user_oid = resp.json()['User']['ObjectId']

            url = '{0}/users/{1}/credential/pin'.format(self.url_base, user_oid)
            body = {'Credentials': new_pin}

            resp = self.cuc.put(url, json=body, timeout=self.timeout)

            if resp.status_code != 204:
                CUPI.status = 'Something went wrong: {0} {1} {2}'.format(resp.status_code, resp.reason, resp.text)
                print(CUPI.status)
                return False
            else:
                CUPI.status = 'Pin updated successfully'
                print(CUPI.status)
                return True
        elif resp.json()['@total'] == '0':
            CUPI.status = 'User directory number not found: {0}'.format(dtmf_access_id)
            print(CUPI.status)
            return False
        else:
            CUPI.status = 'Unknown result: {0} {1} {2}'.format(resp.status_code, resp.reason, resp.text)
            print(CUPI.status)
            return False

    def delete_user(self, user_oid):
        """

        :param user_oid:
        :return:
        """

        url = '{0}/users/{1}'.format(self.url_base, user_oid)
        resp = self.cuc.delete(url, timeout=self.timeout)

        if resp.status_code == 204:
            CUPI.status = 'User deleted'
            print(CUPI.status)
            return True
        elif resp.status_code == 404:
            CUPI.status = 'User not found'
            print(CUPI.status)
            return False
        else:
            CUPI.status = 'Unknown result: {0} {1} {2}'.format(resp.status_code, resp.reason, resp.text)
            print(CUPI.status)
            return False

    def get_call_handler_template_oid(self):
        """
        Method to get the call handler template oid
        :return: call handler template oid
        """

        url = '{0}/callhandlertemplates'.format(self.url_base)
        return self.cuc.get(url, timeout=self.timeout).json()['CallhandlerTemplate']['ObjectId']

    def get_call_handlers(self, mini=True):
        """

        :param mini:
        :return:
        """
        url = '{0}/handlers/callhandlers'.format(self.url_base)
        resp = self.cuc.get(url, timeout=self.timeout)

        if mini:
            return [(i['DisplayName'], i['ObjectId']) for i in resp.json()['Callhandler']]
        else:
            return resp.json()

    def get_call_handler(self, call_handler_oid):
        """

        :param call_handler_oid:
        :return:
        """
        url = '{0}/handlers/callhandlers/{1}'.format(self.url_base, call_handler_oid)
        resp = self.cuc.get(url, timeout=self.timeout)

        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 404:
            return 'Call handler not found'
        else:
            return 'Unknown result: {0} {1} {2}'.format(resp.status_code, resp.reason, resp.text)

    def get_call_handler_greetings(self, call_handler_oid):
        """

        :param call_handler_oid:
        :return:
        """
        url = '{0}/handlers/callhandlers/{1}/greetings'.format(self.url_base, call_handler_oid)
        resp = self.cuc.get(url, timeout=self.timeout)

        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 404:
            return 'Call handler not found'
        else:
            return 'Unknown result: {0} {1} {2}'.format(resp.status_code, resp.reason, resp.text)

    def get_call_handler_greeting(self, call_handler_oid, greeting='Standard'):
        """

        :param call_handler_oid:
        :param greeting:
        :return:
        """
        greetings = ['Alternate', 'Busy', 'Error', 'Internal', 'Off Hours', 'Standard', 'Holiday']
        if greeting not in greetings:
            return 'Invalid greeting: {0}'.format(greeting)

        if greeting == 'Off Hours':
            greeting = 'Off%20Hours'

        url = '{0}/handlers/callhandlers/{1}/greetings/{2}'.format(self.url_base, call_handler_oid, greeting)
        resp = self.cuc.get(url, timeout=self.timeout)

        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 404:
            return 'Call handler not found'
        else:
            return 'Unknown result: {0} {1} {2}'.format(resp.status_code, resp.reason, resp.text)

    def get_caller_input(self, call_handler_oid):
        """

        :param call_handler_oid:
        :return:
        """

        url = '{0}/handlers/callhandlers/{1}/menuentries'.format(self.url_base, call_handler_oid)
        resp = self.cuc.get(url, timeout=self.timeout)

        if resp.json()['@total'] == '0':
            return 'Call handler not found'
        elif resp.status_code == 200:
            return resp.json()['MenuEntry']
        else:
            return 'Unknown result: {0} {1} {2}'.format(resp.status_code, resp.reason, resp.text)

    def add_call_handler(self, display_name, dtmf_access_id, call_handler_template_oid, schedule_set_oid):
        """

        :param display_name:
        :param dtmf_access_id:
        :param call_handler_template_oid:
        :param schedule_set_oid:
        :return:
        """
        url = '{0}/handlers/callhandlers?templateObjectId={1}'.format(self.url_base, call_handler_template_oid)
        body = {
            'DisplayName': display_name,
            'DtmfAccessId': dtmf_access_id,
            'ScheduleSetObjectId': schedule_set_oid,
        }

        resp = self.cuc.post(url, json=body, timeout=self.timeout)
        call_handler_oid = resp.text.split('/')[-1]

        if resp.status_code != 201:
            return 'Cannot add call handler: {0} {1} {2}'.format(resp.status_code, resp.reason, resp.text)
        else:
            return 'Call handler added successfully', call_handler_oid

    def update_call_handler_transfer_options(self, call_handler_oid, transfer_to_dn, rule='Standard', body={}):
        """

        :param transfer_to_dn:
        :param call_handler_oid:
        :param body:
        :param rule:
        :return:
        """

        url = '{0}/handlers/callhandlers/{1}/transferoptions/{2}'.format(self.url_base, call_handler_oid, rule)
        if not body:
            body = {
                'Action': '1',
                'Extension': transfer_to_dn,
                'PlayTransferPrompt': 'false'
            }

        resp = self.cuc.put(url, json=body, timeout=self.timeout)
        if resp.status_code == 204:
            return 'Call handler transfer rule updated'
        else:
            return 'Call handler not updated: {0} {1} {2}'.format(resp.status_code, resp.reason, resp.text)

    def update_call_handler_greeting(self,
                                     call_handler_oid,
                                     user_call_handler_oid,
                                     greeting='Off%20Hours',
                                     time_expires='',
                                     enabled='true',
                                     after_greeting_action='2',
                                     after_greeting_target_con='PHGreeting',
                                     enable_transfer='false',
                                     ignore_digits='true',
                                     play_recorded_msg_prompt='false',
                                     play_what='1',
                                     reprompt_delay='2',
                                     reprompts='0',
                                     body={}):
        """

        :param call_handler_oid:
        :param user_call_handler_oid: get with get_user_call_handler_oid method
        :param greeting:
        :param time_expires: set to '' which equals NULL, used with enabled parameter
        :param enabled: set to true, must be used with time expires set to NULL to work.
                        Note: Standard greeting should never be set to false.
        :param after_greeting_action:
        :param after_greeting_target_con:
        :param enable_transfer:
        :param ignore_digits:
        :param play_recorded_msg_prompt:
        :param play_what:
        :param reprompt_delay:
        :param reprompts:
        :param body:
        :return:
        """
        url = '{0}/handlers/callhandlers/{1}/greetings/{2}'.format(self.url_base, call_handler_oid, greeting)
        if not body:
            body = {
                'TimeExpires': time_expires,
                'Enabled': enabled,
                'AfterGreetingAction': after_greeting_action,
                'AfterGreetingTargetConversation': after_greeting_target_con,
                'AfterGreetingTargetHandlerObjectId': user_call_handler_oid,
                'EnableTransfer': enable_transfer,
                'IgnoreDigits': ignore_digits,
                'PlayRecordMessagePrompt': play_recorded_msg_prompt,
                'PlayWhat': play_what,
                'RepromptDelay': reprompt_delay,
                'Reprompts': reprompts,
            }

        resp = self.cuc.put(url, json=body, timeout=self.timeout)
        if resp.status_code == 204:
            return 'Call handler {0} greeting updated'.format(greeting)
        else:
            return 'Call handler {0} greeting not updated: {1} {2} {3}'.format(
                    greeting, resp.status_code, resp.reason, resp.text)

    def update_call_handler_greeting_recording(self,
                                               call_handler_oid,
                                               greeting,
                                               file_location,
                                               greeting_file,
                                               language='1033'):
        """
        Updating call handler greeting recordings is a 3 part process
        1) create a temp file
        2) upload recording to temp file location
        3) assign tempfile to greeting
        :param call_handler_oid:
        :param greeting:
        :param file_location:
        :param greeting_file:
        :param language: 1033 for english-us
        :return:
        """

        # update headers
        self.cuc.headers.update({
            'Accept': '*/*',
            'Connection': 'keep_alive',
            'Content_type': 'audio/wav',
        })

        # 1) Create a temp file
        url = '{0}/voicefiles'.format(self.url_base)
        resp = self.cuc.post(url, timeout=self.timeout)
        temp_file = resp.text

        if resp.status_code == 201:
            # 2) Upload recording to temp file location
            url = '{0}/voicefiles/{1}'.format(self.url_base, temp_file)

            try:
                with open('{0}/{1}'.format(file_location, greeting_file), 'rb') as payload:
                    resp = self.cuc.put(url, data=payload, timeout=self.timeout)
            except FileNotFoundError:
                return 'File: {0} Not Found'.format(greeting_file)

            if resp.status_code == 204:
                # 3) Assign temp file to greeting
                url = '{0}/handlers/callhandlers/{1}/greetings/{2}/greetingstreamfiles/{3}'.format(
                        self.url_base, call_handler_oid, greeting, language
                )
                body = {'StreamFile': temp_file}

                resp = self.cuc.put(url, json=body, timeout=self.timeout)

                # Return headers to normal
                self.cuc.headers.update({
                    'Accept': 'application/json',
                    'Connection': 'keep_alive',
                    'Content_type': 'application/json',
                })
                if resp.status_code == 204:
                    return '{0} greeting successfully updated'.format(greeting)
                else:
                    return 'Could not update greeting: {0} {1} {2}'.format(
                            resp.status_code, resp.reason, resp.text
                    )

            else:
                return 'Could upload file: {0} {1} {2}'.format(
                        resp.status_code, resp.reason, resp.text
                )
        else:
            return 'Could not create temp file: {0} {1} {2}'.format(
                    temp_file.status_code, temp_file.reason, temp_file.text
            )

    def update_caller_input(self,
                            call_handler_oid,
                            target_call_handler_oid,
                            input_key='1',
                            action='2',
                            target_conversation='PHGreeting',
                            body={}):
        """

        :param call_handler_oid:
        :param target_call_handler_oid: Target users call handler oid.
                                        Get with get_user_call_handler_oid method
        :param input_key:
        :param action:
        :param target_conversation:
        :param body:
        :return:
        """

        url = '{0}/handlers/callhandlers/{1}/menuentries/{2}'.format(self.url_base, call_handler_oid, input_key)
        if not body:
            body = {
                'Action': action,
                'TargetConversation': target_conversation,
                'TargetHandlerObjectId': target_call_handler_oid,
            }

        resp = self.cuc.put(url, json=body, timeout=self.timeout)
        if resp.status_code == 204:
            return 'Call handler caller input updated'
        else:
            return 'Call handler caller input not updated: {1} {2} {3}'.format(
                    resp.status_code, resp.reason, resp.text)

    def delete_call_handler(self, call_handler_oid):
        """

        :param call_handler_oid:
        :return:
        """

        url = '{0}/handlers/callhandlers/{1}'.format(self.url_base, call_handler_oid)
        resp = self.cuc.delete(url, timeout=self.timeout)

        if resp.status_code == 204:
            return 'Call handler deleted'
        elif resp.status_code == 404:
            return 'Call handler not found'
        else:
            return 'Unknown result: {0} {1} {2}'.format(resp.status_code, resp.reason, resp.text)

