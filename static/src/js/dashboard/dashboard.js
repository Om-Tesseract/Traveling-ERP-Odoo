/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component, onWillStart,onWillUpdateProps, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
export class Dashboard extends Component {

setup() {
super.setup();
this.orm = useService("orm");
this.state = useState({hierarchy: {}}); 
}

}
Dashboard.template = "dashboard_template";
registry.category("actions").add("travel_dashboard", Dashboard);