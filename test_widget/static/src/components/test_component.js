import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";
import { InputVerificationCodeComponent } from "@test_widget/components/input_verification_code_component";
import { useService } from "@web/core/utils/hooks";


class TestComponent extends Component {
    static template = "test_widget.testComponent";
    static props = standardActionServiceProps;
    static components = {
        InputVerificationCodeComponent,
    }

    setup() {
        this.action = useService("action");
    }

    async onFilled(verificationCode) {
        console.log(verificationCode);
        this.action.doAction({ 'type': 'ir.actions.act_window_close'});
    }
}

registry.category("actions").add("test_widget.test_action", TestComponent);
