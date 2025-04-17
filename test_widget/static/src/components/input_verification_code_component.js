import { Component, useRef } from "@odoo/owl";

export class InputVerificationCodeComponent extends Component {
    static template = "test_widget.inputVerificationCodeComponent";
    static props = {
        nbInputs: Number,
        onFilled: Function,
    };

    setup() {
        this.inputLst = [];
        for (let i = 0; i < this.props.nbInputs; i++) {
            this.inputLst.push(useRef(`input_${i}`));
        }
    }

    onFocus(ev) {
        const input_el = ev.target;
        input_el.setSelectionRange(0, input_el.value.length);
    }

    onInput(ev) {
        if (this.verificationCode.length === this.props.nbInputs) {
            this.props.onFilled(this.verificationCode);
        }

        const i = this.getInputIndex(ev.target);
        if (i < this.props.nbInputs - 1 && ev.target.value.length === 1) {
            this.inputLst[i + 1].el.focus();
        }
    }

    onPaste(ev) {
        if(!ev.clipboardData?.items) {
            return;
        }

        ev.preventDefault();

        let pastedData = ev.clipboardData.getData('text').split('');
        const start_index = this.getInputIndex(ev.target);
        for (const input of this.inputLst.slice(start_index)) {
            const input_el = input.el;
            input_el.value = pastedData.shift() || "";
            this.onInput({ target: input_el });
        }
    }

    onKeydown(ev) {
        const i = this.getInputIndex(ev.target);
        if (ev.key === 'Backspace' && ev.target.value === "" && i > 0) {
            ev.preventDefault();
            const new_focused_el = this.inputLst[i - 1].el;
            new_focused_el.focus();
            new_focused_el.value = "";
        } else if (ev.key === 'ArrowLeft') {
            ev.preventDefault();
            const indexToFocus = (i > 0) ? i - 1 : 0;
            this.inputLst[indexToFocus].el.focus();
        } else if (ev.key === 'ArrowRight') {
            ev.preventDefault();
            const indexToFocus = (i < this.props.nbInputs - 1) ? i + 1 : i;
            this.inputLst[indexToFocus].el.focus();
        }
    }

    get verificationCode() {
        let verificationCode = "";

        for (const input of this.inputLst) {
            const value = input.el.value;
            if (value) {
                verificationCode += value;
            }
        }

        return verificationCode;
    }

    getInputIndex(el) {
        return this.inputLst.findIndex(input => input.el == el);
    }

}
