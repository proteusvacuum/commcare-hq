hqDefine("data_interfaces/js/auto_update_rules", [
    'jquery',
    'knockout',
    'underscore',
    'hqwebapp/js/initial_page_data',
    'analytix/js/google',
    'hqwebapp/js/components.ko', // for pagination
], function (
    $,
    ko,
    _,
    initialPageData,
    googleAnalytics
) {

    var RuleViewModel = function (data) {
        var self = {};
        self.action_error = null;
        self.active = data.active;
        self.caseType = data.case_type;
        self.editURL = data.edit_url;
        self.id = data.id;
        self.lastRun = data.last_run;
        self.name = data.name;
        self.status = data.status;
        return self;
    };

    var RuleListViewModel = function (rules) {
        var self = {};
        self.rules = ko.observableArray(_.map(rules, RuleViewModel));
        self.paginatedRules = ko.observableArray([]);
        self.rulesById = ko.computed(function () {
            return _.indexBy(self.rules(), 'id');
        });

        // pagination
        self.itemsPerPage = ko.observable(5);
        self.totalItems = ko.computed(function () {
            return self.rules().length;
        });
        self.currentPage = 1;

        self.goToPage = function (page) {
            self.currentPage = page;
            self.paginatedRules.removeAll();
            var skip = (self.currentPage - 1) * self.itemsPerPage();
            self.paginatedRules(self.rules().slice(skip, skip + self.itemsPerPage()));
        };

        self.onPaginationLoad = function () {
            self.goToPage(1);
        };

        // actions
        self.deleteRule = function (rule) {
            $.ajax({
                url: "",
                type: "POST",
                dataType: 'json',
                data: {
                    action: 'delete',
                    id: rule.id,
                },
                success: function (data) {
                    if (data.success) {
                        self.rules.remove(rule);
                        self.goToPage(1);
                    } else {
                        self.showActionError(rule, data.error);
                    }
                },
                error: function () {
                    self.showActionError(rule, gettext("Issue communicating with server. Try again."));
                },
            });
        };

        self.updateRule = function (action, rule) {
            $.ajax({
                url: "",
                type: "POST",
                dataType: 'json',
                data: {
                    action: action,
                    id: rule.id,
                },
                success: function (data) {
                    if (data.success) {
                        self.rules.remove(rule);
                        var updatedRule = RuleViewModel(data.itemData);
                        self.rules.push(updatedRule);
                        self.rules().sort(function (first, second) {
                            var firstName = first.name.toUpperCase();
                            var secondName = second.name.toUpperCase();
                            if (firstName > secondName) {
                                return 1;
                            } else if (firstName < secondName) {
                                return -1;
                            } else {
                                return 0;
                            }
                        });
                        self.goToPage(1);
                    } else {
                        self.showActionError(rule, data.error);
                    }
                },
                error: function () {
                    self.showActionError(rule, gettext("Issue communicating with server. Try again."));
                },
            });
        };

        self.showActionError = function (rule, error) {
            var ruleToUpdate = self.rulesById()[rule.id];
            ruleToUpdate.action_error = error;
            self.rules.valueHasMutated();
        };

        return self;
    };

    $(function () {
        var rules = initialPageData.get('rules');
        var viewModel = RuleListViewModel(rules);
        $("#ko-auto-update-rules").koApplyBindings(viewModel);

        $("#add-new").click(function () {
            googleAnalytics.track.event('Automatic Case Closure', 'Rules', 'Set Rule');
        });
    });
});
