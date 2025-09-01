import { onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";
import { FloatField } from "@web/views/fields/float/float_field";

patch(FloatField.prototype, {
    setup() {
        this.orm = useService("orm");
        onWillStart(async () => {
            if (this.props.name === 'no_precision') {
                this.minDecimals = await this.orm.call(
                    "decimal.precision",
                    "precision_get",
                    ['Yo_Yo_Yo_Yo_Yo_Yo_Yo'],
                );
            }
        })
        super.setup();
    },

    get formattedValue() {
        if (this.props.name === 'no_precision') {
            const [_intPart, decPart = ""] = this.value.toString().split(".");
            let digits;
            if (decPart.length < this.minDecimals) {
                digits = this.minDecimals;
            } else {
                digits = Math.min(8, decPart.length);
            }
            this.props.digits = [16, digits];
        }
        return super.formattedValue;
    }
});
