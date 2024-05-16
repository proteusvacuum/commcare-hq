"use strict";
hqDefine('accounting/js/renew_plan_selection', [
    'jquery',
    'knockout',
    'hqwebapp/js/initial_page_data',
    'hqwebapp/js/toggles',
], function (
    $,
    ko,
    initialPageData,
    toggles
) {
    const PlanRenewalView = function (options) {
        const self = this;
        self.monthlyPlan = options.renewalChoices.monthly_plan;
        self.annualPlan = options.renewalChoices.annual_plan;
        self.showAnnualPlan = ko.observable(options.isAnnualPlan);
        self.selectedPlan = ko.pureComputed(() => {
            return self.showAnnualPlan() ? self.annualPlan : self.monthlyPlan;
        });
    };

    $(function () {
        if (toggles.toggleEnabled('SELF_SERVICE_ANNUAL_RENEWALS')) {
            const planRenewalView = new PlanRenewalView({
                renewalChoices: initialPageData.get('renewal_choices'),
                isAnnualPlan: initialPageData.get('is_annual_plan'),
            });

            $('#renew-plan-selection').koApplyBindings(planRenewalView);
        }
    });
});
