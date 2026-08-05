import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

import { RecordSelector } from "@web/core/record_selectors/record_selector";

class TestComponent extends Component {
    static template = "test_record_selector.testComponent";
    static props = standardActionServiceProps;
    static components = {
        RecordSelector,
    }

    get recordSelectorProps() {
        return {
            resId: false,
            resModel: "res.partner",
            update: () => {},
        }
    }

}

registry.category("actions").add("test_record_selector.test_action", TestComponent);
