/** @odoo-module **/
import { Component, onWillStart, useState, onMounted, onWillUnmount  } from "@odoo/owl";

export class DataGridComponent extends Component {
  static template = "travels_erp.DynamicDataGridTemplate";

  setup() {
    this.sortColumn = this.sortColumn.bind(this);
    this.getSortClass = this.getSortClass.bind(this);
    this.toggleColumn = this.toggleColumn.bind(this);
    this.onMouseDown = this.onMouseDown.bind(this);
    this.onMouseMove = this.onMouseMove.bind(this);
    this.onMouseUp = this.onMouseUp.bind(this);
    this.mounted = this.mounted.bind(this);
    this.willUnmount = this.willUnmount.bind(this);

    // If you need to manipulate or fetch data, do it in onWillStart or setup
    // onWillStart(async () => {
    //     this.state.data = this.props.data || [];
    //     console.log('Initial data:', this.state.data); // Should show initial data or empty array

    // });
    onMounted(()=>{
        this.mounted()
    })
    onWillUnmount(()=>{
        this.willUnmount()
    })

  }
  sortColumn(columnKey) {
    console.log(columnKey);
    if (this.props.onSort) {
      this.props.onSort(columnKey);
    }
  }
  getSortClass(columnKey) {
    if (this.props.sortColumn === columnKey) {
      return `fa fa-sort-${this.props.sortDirection}`;
    }
    return "fa fa-sort"; // Default sort icon
  }
  toggleColumn(columnKey) {
    const column = this.props.columns.find(
      (column) => column.key === columnKey
    );
    if (column) {
      column.option = !column.option; // Toggle the option
    }
    console.log(this.props.columns.find((column) => column.key === columnKey));
  }
  mounted() {
    this.resizeHandle = null;
    this.startX = 0;
    this.startWidth = 0;

    const resizeHandles = document.querySelectorAll('.resize-handle');
    resizeHandles.forEach(handle => {
        handle.addEventListener('mousedown', this.onMouseDown);
    });

    document.addEventListener('mousemove', this.onMouseMove);
    document.addEventListener('mouseup', this.onMouseUp);
}

onMouseDown(event) {
    this.resizeHandle = event.target;
    this.startX = event.clientX;

    const th = this.resizeHandle.parentElement.parentElement;
    this.startWidth = th.offsetWidth;
}

onMouseMove(event) {
    if (!this.resizeHandle) return;

    const dx = event.clientX - this.startX;
    const newWidth = this.startWidth + dx;
    this.resizeHandle.parentElement.parentElement.style.width = `${newWidth}px`;
}

onMouseUp() {
    this.resizeHandle = null;
}

willUnmount() {
    const resizeHandles = document.querySelectorAll('.resize-handle');
    resizeHandles.forEach(handle => {
        handle.removeEventListener('mousedown', this.onMouseDown);
    });

    document.removeEventListener('mousemove', this.onMouseMove);
    document.removeEventListener('mouseup', this.onMouseUp);
}
}
