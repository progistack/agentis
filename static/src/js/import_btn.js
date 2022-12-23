odoo.define('agentis.ImportBtn', function(require){
    "use strict"

var core = require('web.core');
var _t = core._t;
var ListController = require('web.ListController');

    ListController.include({
       renderButtons: function($node) {
       this._super.apply(this, arguments);
           if (this.$buttons) {
             this.$buttons.find('.o_list_button_export').click(this.proxy('action_export'));
           }
        },

        //--------------------------------------------------------------------------
        // Define Handler for new Custom Button
        //--------------------------------------------------------------------------

        /**
         * @private
         * @param {MouseEvent} event
         */
        action_export: function (e) {
            var self = this;
            var active_id = this.model.get(this.handle).getContext()['active_ids'];
            var model_name = this.model.get(this.handle).getContext()['active_model'];
                this._rpc({
                        model: 'agentis.dga',
                        method: 'export_operation',
                        args: [self.inventory_id],
                    }).then(function (result) {
                        result.do_action()
                    });
          },
          action_validate: function (e) {
                var self = this;
                var prom = Promise.resolve();
                var recordID = this.renderer.getEditableRecordID();
                console.log('recodeeeeeeeeee',recordID)
                if (recordID) {

                    prom = this.saveRecord(recordID);
                }

                prom.then(function () {
                    self._rpc({
                        model: 'stock.inventory',
                        method: 'action_validate',
                        args: [self.inventory_id]
                    }).then(function (res) {
                        var exitCallback = function (infos) {
                            // In case we discarded a wizard, we do nothing to stay on
                            // the same view...
                            if (infos && infos.special) {
                                return;
                            }
                            // ... but in any other cases, we go back on the inventory form.
                            self.do_notify(
                                false,
                                _t("The inventory has been validated"));
                            self.trigger_up('history_back');
                        };

                        if (_.isObject(res)) {
                            self.do_action(res, { on_close: exitCallback });
                        } else {
                            return exitCallback();
                        }
                    });
                });

             },


    });


});