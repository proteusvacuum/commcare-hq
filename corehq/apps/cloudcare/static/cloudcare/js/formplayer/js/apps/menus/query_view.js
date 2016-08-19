/*global FormplayerFrontend */

FormplayerFrontend.module("SessionNavigate.MenuList", function (MenuList, FormplayerFrontend, Backbone, Marionette) {
    MenuList.QueryView = Marionette.ItemView.extend({
        tagName: "tr",
        className: "formplayer-request",
        template: "#query-view-item-template",

        templateHelpers: function () {
            var imageUri = this.options.model.get('imageUri');
            var audioUri = this.options.model.get('audioUri');
            var appId = this.model.collection.appId;
            return {
                imageUrl: imageUri ? FormplayerFrontend.request('resourceMap', imageUri, appId) : "",
                audioUrl: audioUri ? FormplayerFrontend.request('resourceMap', audioUri, appId) : "",
            };
        },
    });

    MenuList.QueryListView = Marionette.CompositeView.extend({
        tagName: "div",
        template: "#query-view-list-template",
        childView: MenuList.QueryView,
        childViewContainer: "tbody",

        initialize: function(options) {
            this.parentModel = options.collection.models;
        },

        templateHelpers: function () {
            return {
                title: this.options.title,
            };
        },

        ui: {
            submitButton: '#query-submit-button',
        },

        events: {
            'click @ui.submitButton': 'submitAction',
        },

        submitAction: function() {
            var payload = {};
            var fields = $(".query-field");
            var model = this.parentModel;
            fields.each(function(index) {
                payload[model[index].get('id')] = this.value;
            });
            FormplayerFrontend.trigger("menu:query", payload);
        },
    });
});