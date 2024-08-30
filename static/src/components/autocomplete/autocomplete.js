/** @odoo-module **/
import { Component, useState } from "@odoo/owl";

export class AutoComplete extends Component {
    static template = "travels_erp.AutocompleteTemplate";

    setup() {
        this.state = useState({
            isDropdownVisible: false,
            inputValue: this.props.value ? this.props.value:''
        });
        this.debouncedOnChangeInput = this.debounce(this.onChangeInput.bind(this), 300);

        // this.onChangeInput = this.onChangeInput.bind(this);
        this.onClickSelect = this.onClickSelect.bind(this);
    }

    debounce(func, wait) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }
    
    onFocusInput(){
        this.state.isDropdownVisible = true;

    }
    onChangeInput(e) {
        const value = e.target.value;
        this.state.inputValue = value;
        this.state.isDropdownVisible = true;
        this.props.onchange(e); // Notify the parent of the change
    }

    onClickSelect(val) {
        this.state.inputValue = val.label;
        this.state.isDropdownVisible = false;
        console.log(val,this.props.row_id);
        this.props.onSelect(val,this.props.row_id)
       
    }
}
