@AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_maintenancewindow(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'mc_path': _get_test_data_file('maintenancewindow.json'),
            'auto_upgrade_config_name': 'aksManagedAutoUpgradeSchedule',
            'node_os_upgrade_config_name': 'aksManagedNodeOSUpgradeSchedule',
            'ssh_key_value': self.generate_ssh_keys(),
            'future_date': "2123-01-01" 
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --ssh-key-value={ssh_key_value}'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded')
        ])

        # add dedicated maintenanceconfiguration for cluster autoupgrade
        maintenance_configuration_add_cmd = 'aks maintenanceconfiguration add ' \
            '-g {resource_group} --cluster-name {name} ' \
            '-n {auto_upgrade_config_name} ' \
            '--schedule-type Weekly ' \
            '--day-of-week Friday ' \
            '--interval-weeks 3 ' \
            '--duration 8 ' \
            '--utc-offset +05:30 ' \
            '--start-date {future_date} ' \
            '--start-time 00:00 ' 

        self.cmd(
            maintenance_configuration_add_cmd, checks=[
                self.exists('maintenanceWindow.schedule.weekly'),
                self.check('maintenanceWindow.schedule.weekly.dayOfWeek', 'Friday'),
                self.check('maintenanceWindow.schedule.weekly.intervalWeeks', 3),
                self.check('maintenanceWindow.durationHours', 8),
                self.check('maintenanceWindow.utcOffset', '+05:30'),
                self.check('maintenanceWindow.startDate', '{future_date}'),
                self.check('maintenanceWindow.startTime', '00:00')]
        )

        # add dedicated maintenanceconfiguration for node os autoupgrade
        maintenance_configuration_add_cmd = 'aks maintenanceconfiguration add ' \
            '-g {resource_group} --cluster-name {name} ' \
            '-n {node_os_upgrade_config_name} ' \
            '--schedule-type RelativeMonthly ' \
            '--day-of-week Tuesday ' \
            '--week-index Last ' \
            '--interval-months 1 ' \
            '--duration 12 ' \
            '--start-time 09:00 ' \
            '--utc-offset=-08:00 ' \
            '--start-date {future_date} '

        self.cmd(
            maintenance_configuration_add_cmd, checks=[
                self.exists('maintenanceWindow.schedule.relativeMonthly'),
                self.check('maintenanceWindow.schedule.relativeMonthly.dayOfWeek', 'Tuesday'),
                self.check('maintenanceWindow.schedule.relativeMonthly.intervalMonths', 1),
                self.check('maintenanceWindow.durationHours', 12),
                self.check('maintenanceWindow.utcOffset', '-08:00'),
                self.check('maintenanceWindow.startDate', '{future_date}'),
                self.check('maintenanceWindow.startTime', '09:00')]
        )

        # maintenanceconfiguration list
        maintenance_configuration_list_cmd = 'aks maintenanceconfiguration list ' \
            '-g {resource_group} --cluster-name {name}'
        self.cmd(maintenance_configuration_list_cmd, checks=[self.check('length(@)', 2)])

        # update maintenanceconfiguration from config file
        maintenance_configuration_update_cmd = 'aks maintenanceconfiguration update ' \
            '-g {resource_group} --cluster-name {name} ' \
            '-n {auto_upgrade_config_name} ' \
            '--config-file {mc_path}'

        self.cmd(
            maintenance_configuration_update_cmd, checks=[
                self.exists('maintenanceWindow.schedule.absoluteMonthly'),
                self.check('maintenanceWindow.schedule.absoluteMonthly.dayOfMonth', 1),
                self.check('maintenanceWindow.schedule.absoluteMonthly.intervalMonths', 3),
                self.check('maintenanceWindow.durationHours', 4),
                self.check('maintenanceWindow.utcOffset', '-08:00'),
                self.check('maintenanceWindow.startTime', '09:00'), 
                self.check('maintenanceWindow.notAllowedDates | length(@)', 2)]
        )

        # maintenanceconfiguration show
        maintenance_configuration_show_cmd = 'aks maintenanceconfiguration show ' \
            '-g {resource_group} --cluster-name {name} ' \
            '-n {auto_upgrade_config_name}'
        self.cmd(
            maintenance_configuration_show_cmd, checks=[
                self.check("name == '{auto_upgrade_config_name}'", True)]
        )

        # maintenanceconfiguration delete
        maintenance_configuration_delete_cmd = 'aks maintenanceconfiguration delete ' \
            '-g {resource_group} --cluster-name {name} ' \
            '-n {auto_upgrade_config_name}'
        self.cmd(maintenance_configuration_delete_cmd, checks=[self.is_empty()])

        maintenance_configuration_delete_cmd = 'aks maintenanceconfiguration delete ' \
            '-g {resource_group} --cluster-name {name} ' \
            '-n {node_os_upgrade_config_name}'
        self.cmd(maintenance_configuration_delete_cmd, checks=[self.is_empty()])
        
        # maintenanceconfiguration list
        maintenance_configuration_list_cmd = 'aks maintenanceconfiguration list ' \
            '-g {resource_group} --cluster-name {name}'
        self.cmd(maintenance_configuration_list_cmd, checks=[self.is_empty()])

        # delete
        self.cmd('aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_maintenanceconfiguration(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'mc_path': _get_test_data_file('maintenanceconfig.json'),
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --ssh-key-value={ssh_key_value}'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded')
        ])

        # maintenanceconfiguration add
        maintenance_configuration_add_cmd = 'aks maintenanceconfiguration add -g {resource_group} --cluster-name {name} -n default --weekday Monday --start-hour 1'
        self.cmd(
            maintenance_configuration_add_cmd, checks=[
                self.check('timeInWeek[0].day', 'Monday'),
                self.check('timeInWeek[0].day', 'Monday'),
                self.check('timeInWeek[0].hourSlots | contains(@, `1`)', True)]
        )

        # maintenanceconfiguration update (from config file)
        maintenance_configuration_update_cmd = 'aks maintenanceconfiguration update -g {resource_group} --cluster-name {name} -n default --config-file {mc_path}'
        self.cmd(
            maintenance_configuration_update_cmd, checks=[
                self.check(
                    "timeInWeek[*].day | contains(@, 'Tuesday') && contains(@, 'Wednesday')", True),
                self.check(
                    "timeInWeek[*].hourSlots[*] | contains([0], `2`) && contains([1], `6`)", True),
                self.check("notAllowedTime | length(@) == `2`", True)]
        )

        # maintenanceconfiguration show
        maintenance_configuration_show_cmd = 'aks maintenanceconfiguration show -g {resource_group} --cluster-name {name} -n default'
        self.cmd(
            maintenance_configuration_show_cmd, checks=[
                self.check("name == 'default'", True)]
        )

        # maintenanceconfiguration delete
        maintenance_configuration_delete_cmd = 'aks maintenanceconfiguration delete -g {resource_group} --cluster-name {name} -n default'
        self.cmd(
            maintenance_configuration_delete_cmd, checks=[self.is_empty()])

        # maintenanceconfiguration list
        maintenance_configuration_list_cmd = 'aks maintenanceconfiguration list -g {resource_group} --cluster-name {name}'
        self.cmd(
            maintenance_configuration_list_cmd, checks=[self.is_empty()])

        # delete
        self.cmd(
            'aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])
