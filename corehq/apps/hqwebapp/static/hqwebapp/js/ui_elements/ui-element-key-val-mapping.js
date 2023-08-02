/**
    Key-value mapping UI element.

    This element generates a button that pops up a modal containing pairs of keys and values.
    Expects to be used in app manager, in the context of an application module.
    Used primarily in case list/detail display properties. Keys may be strings
    (as in ID Mapping format) or calcuations (as in Conditional ID Mapping format).
    Values may be strings (as in both ID Mapping formats) or references to images
    (as in Icon format). Supports translations.

    Options:
        Required:
            items: Array of current values. Each item should be the javascript equivalent
                of a MappingItem.
            lang: Current language.
            langs: All languages.
            property_name: Observable representing the name of the overall mapping.
                May be either a string or one of the elements defined in hqwebapp/js/ui-element.
                Used primarily to add title to modal. If values_are_icons, this should be a slug.
        Optional:
            keys_are_conditions: True iff KEYS are calculations rather than strings.
            values_are_icons: True iff values are image references ("jr://file...")
            module_id: Module id, should be provided if values_are_icons is being used in a module context
                (e.g., case list/detail config).
            multimedia: Only needed if values_are_icons. Object containing multimedia
                to be passed as appMenuMediaManager's objectMap. Keys are image references;
                values are objects as generated by CommCareMultimedia.get_media_info
            buttonText: Text for button that opens modal. Defaults to "Edit".
 */
hqDefine('hqwebapp/js/ui_elements/ui-element-key-val-mapping', function () {
    'use strict';
    var module = {};

    // To autogenerate cssid from random string
    // copied from http://stackoverflow.com/questions/7627000/javascript-convert-string-to-safe-class-name-for-css
    var makeSafeForCSS = function (name) {
        if (!name) {
            return "";
        }
        return name.replace(/[^a-z0-9]/g, function (s) {
            var c = s.charCodeAt(0);
            if (c === 32) return '-';
            if (c >= 65 && c <= 90) return '_' + s.toLowerCase();
            return '__' + ('000' + c.toString(16)).slice(-4);
        });
    };

    /**
    * MapItem is a ko representation for `item` objects.
    *
    * @param item: a raw object which contains keys called `key` and `value`.
    *              the `value` in a item itself is an object, a mapping
    *              of language codes to strings
    * @param mappingContext: an object which has context of current UI language and whether
    *                 `value` of MapItem is a file-path to an icon or a simple string
    */
    var MapItem = function (item, index, mappingContext) {
        var self = {};
        self.key = ko.observable(item.key);
        self.editing = ko.observable(false);

        self.cssId = ko.computed(function () {
            return makeSafeForCSS(self.key()) || '_blank_';
        });


        // util function to generate icon-name of the format "module<module_id>_list_icon_<property_name>_<hash_of_item.key>"
        self.generateIconPath = function () {
            var randomFourDigits = Math.floor(Math.random() * 9000) + 1000;
            var iconPrefix =  "jr://file/commcare/image/module" + mappingContext.module_id + "_list_icon_" + mappingContext.getPropertyName() + "_";
            return iconPrefix + randomFourDigits + ".png";
        };


        var app_manager = hqImport('app_manager/js/app_manager_media');
        var uploaders = hqImport("app_manager/js/nav_menu_media_common");
        // attach a media-manager if item.value is a file-path to icon
        if (mappingContext.values_are_icons()) {
            var actualPath = item.value[mappingContext.lang];
            var defaultIconPath = actualPath || self.generateIconPath();
            self.iconManager = app_manager.appMenuMediaManager({
                ref: {
                    "path": actualPath,
                    "icon_type": "icon-picture",
                    "media_type": "Image",
                    "media_class": "CommCareImage",
                    "icon_class": "icon-picture",
                },
                objectMap: mappingContext.multimedia,
                uploadController: uploaders.iconUploader,
                defaultPath: defaultIconPath,
                inputElement: $("#" + self.cssId()),
            });
        }

        self.toggleEditMode = function () {
            self.editing(!self.editing());
        };

        self.value = ko.computed(function () {
            // ko.observable for item.value
            var new_value = [];
            var langs = _.union(_(item.value).keys(), [mappingContext.lang]) ;
            _.each(langs, function (lang) {
                // return ko reference to path in `iconManager` for current UI language value
                if (mappingContext.values_are_icons() && lang === mappingContext.lang) {
                    new_value.push([lang, self.iconManager.customPath]);
                }
                // return new ko.observable for other languages
                else {
                    new_value.push([lang, ko.observable(item.value[lang])]);
                }
            });
            return _.object(new_value);
        });

        self.key.subscribe(function (newValue) {
            if (mappingContext.duplicatedItems.indexOf(newValue) === -1 && mappingContext._isItemDuplicated(newValue)) {
                mappingContext.duplicatedItems.push(newValue);
            }

        });

        self.key.subscribe(function (oldValue) {
            var index = mappingContext.duplicatedItems.indexOf(oldValue);
            if (index !== -1 && !mappingContext._isItemDuplicated(oldValue, 2)) {
                mappingContext.duplicatedItems.remove(oldValue);
            }
        }, null, "beforeChange");

        return self;
    };

    /**
     * A MapList is an ordered list of MapItem objects
     */
    var MapList = function (options) {
        hqImport("hqwebapp/js/assert_properties").assert(options, [
            'lang',
            'langs',
            'items',
            'property_name',
        ], [
            'buttonText',
            'keys_are_conditions',
            'module_id',
            'multimedia',
            'values_are_icons',
        ]);

        var self = {};
        self.lang = options.lang;
        self.langs = [options.lang].concat(options.langs);
        self.module_id = options.module_id;
        self.items = ko.observableArray();
        self.duplicatedItems = ko.observableArray();
        self.values_are_icons = ko.observable(options.values_are_icons || false);
        self.keys_are_conditions = ko.observable(options.keys_are_conditions || false);
        self.multimedia = options.multimedia;

        self.getPropertyName = function () {
            if (_.isObject(options.property_name) && _.isFunction(options.property_name.val)) {
                return options.property_name.val();
            }
            return options.property_name;
        };

        self.labels = ko.computed(function () {
            if (self.values_are_icons()) {
                return {
                    placeholder: gettext('Calculation'),
                    duplicated: gettext('Calculation is duplicated'),
                    addButton: gettext('Add Image'),
                    badXML: gettext('Calculation contains an invalid character.'),
                };
            }
            else if (self.keys_are_conditions()) {
                return {
                    placeholder: gettext('Calculation'),
                    duplicated: gettext('Calculation is duplicated'),
                    addButton: gettext('Add Key, Value Mapping'),
                    badXML: gettext('Calculation contains an invalid character.'),
                };
            }
            else {
                return {
                    placeholder: gettext('Key'),
                    duplicated: gettext('Key is duplicated'),
                    addButton: gettext('Add Key, Value Mapping'),
                    badXML: gettext('Key contains an invalid character.'),
                };
            }
        });

        self.setItems = function (items) {
            self.items(_(items).map(function (item, i) {
                return new MapItem(item, i, self);
            }));
        };
        self.setItems(options.items);

        self.backup = function (value) {
            var backup;
            for (var i = 0; i < self.langs.length; i += 1) {
                var lang = self.langs[i];
                backup = value[lang];
                if (backup && backup() !== '') {
                    return {lang: lang, value: backup()};
                }
            }
            return {lang: null, value: 'value'};
        };
        self.removeItem = function (item) {
            self.items.remove(item);
            if (!self._isItemDuplicated(ko.utils.unwrapObservable(item.key)))
                self.duplicatedItems.remove(ko.utils.unwrapObservable(item.key));
        };
        self.addItem = function () {
            var raw_item = {key: '', value: {}};
            raw_item.value[self.lang] = '';

            var item = new MapItem(raw_item, self.items.length, self);
            self.items.push(item);
            if (self.duplicatedItems.indexOf('') === -1 && self._isItemDuplicated('')) {
                self.duplicatedItems.push('');
            }
        };

        self._isItemDuplicated = function (key, max_counts) {
            if (typeof(max_counts) === 'undefined') max_counts = 1;
            var items = self.getItems();
            var counter = 0;
            for (var i = 0; i < items.length; i++) {
                var item = items[i];
                if (ko.utils.unwrapObservable(item.key) === key) {
                    counter++;
                    if (counter > max_counts) return true;
                }
            }
            return false;
        };

        self.isItemDuplicated = function (key) {
            return self.duplicatedItems.indexOf(key) !== -1;
        };

        self.hasBadXML = function (key) {
            if (self.values_are_icons() || self.keys_are_conditions()) {
                // Expressions can contain whatever
                return false;
            }

            // IDs shouldn't have invalid XML characters
            return key.match(/[&<>"']/);
        };

        self.keyHasError = function (key) {
            return self.isItemDuplicated(key) || self.hasBadXML(key);
        };

        self.hasError = function () {
            return self.duplicatedItems().length > 0
                || _.find(self.items(), function (i) { return self.hasBadXML(i.key()); });
        };

        self.getItems = function () {
            return _(self.items()).map(function (item) {
                return {
                    key: ko.utils.unwrapObservable(item.key),
                    value: _.object(_(item.value()).map(function (value, lang) {
                        return [lang, ko.utils.unwrapObservable(value)];
                    })),
                };
            });
        };

        return self;
    };

    module.new = function (options) {
        var m = MapList(options);
        m.edit = ko.observable(true);
        m.buttonText = options.buttonText || gettext("Edit"),
        m.values_are_icons = ko.observable(options.values_are_icons || false);
        m.keys_are_conditions = ko.observable(options.keys_are_conditions || false);
        m.openModal = function () {
            // create a throw-away modal every time
            // lets us create a sandbox for editing that you can cancel
            var $modalDiv = $(document.createElement("div"));
            $modalDiv.attr("data-bind", "template: 'key_value_mapping_modal'");
            var copy = MapList({
                lang: options.lang,
                langs: options.langs,
                module_id: options.module_id,
                items: m.getItems(),
                values_are_icons: m.values_are_icons(),
                keys_are_conditions: m.keys_are_conditions(),
                multimedia: m.multimedia,
                property_name: options.property_name,
            });
            $modalDiv.koApplyBindings({
                modalTitle: ko.computed(function () {
                    return _.template(gettext('Edit mapping for "<%- property %>"'))({
                        property: m.getPropertyName(),
                    });
                }),
                mapList: copy,
                save: function (data, e) {
                    if (copy.duplicatedItems().length > 0) {
                        e.stopImmediatePropagation();
                    } else {
                        m.setItems(copy.getItems());
                    }
                },
            });

            var $modal = $modalDiv.find('.modal');
            $modal.appendTo('body');
            $modal.modal({
                show: true,
                backdrop: 'static',
            });
            $modal.on('hidden', function () {
                $modal.remove();
            });
        };
        m.setEdit = function (edit) {
            m.edit(edit);
        };
        var $div = $(document.createElement("div"));
        $div.attr("data-bind", "template: \'key_value_mapping_template\'");
        $div.koApplyBindings(m);
        m.ui = $div;
        hqImport("hqwebapp/js/bootstrap3/main").eventize(m);
        m.items.subscribe(function () {
            m.fire('change');
        });
        return m;
    };

    return module;

});
