/** @odoo-module **/
import { registry } from "@web/core/registry";
import {
  Component,
  onWillStart,
  onWillUpdateProps,
  onMounted,
  useState,
  markup,
} from "@odoo/owl";
import { DataGridComponent } from "../../components/table/datagrid";
import { AutoComplete } from "../../components/autocomplete/autocomplete";
import { useService } from "@web/core/utils/hooks";
import { FormViewDialog } from "@web/views/view_dialogs/form_view_dialog";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
export class Itineraries extends Component {
  setup() {
    super.setup();
    this.orm = useService("orm");
    this.dialog = useService("dialog");
    this.notification = useService("notification");
    this.action = useService("action");
    this.rpc = useService("rpc");
    this.state = useState({
      data: [],
      columns: [
        {
          name: "Name",
          key: "package_name",
          sortable: true,
        },
        {
          name: "Leaving on",
          key: "leaving_on",
          sortable: true,
        },
        {
          name: "Customer Name",
          key: "customer_name",
          sortable: true,
        },
        {
          name: "Status",
          key: "status",
          sortable: true,
          option: true,
        },
        {
          name: "Actions",

          sortable: false,

          renderCell: (row) => {
            return markup(`
                      <div class="d-flex justify-content-evenly align-items-center">
                      <button type="button" class="btn btn-primary " rounded-5  mt-1 title="Edit" data-id="${row.id}" data-action="edit">
                          <i class="fa fa-edit  "></i> 
                      </button>
                      <button type="button" class="btn btn-danger title="Delete" mt-1  btn-sm"  data-id="${row.id}" data-action="delete">
                          <i class="fa fa-trash"></i> 
                      </button>
                      </div>
                   
                  `);
          },
        },
      ],
      isDropdownVisible: false,
      Options: [],
      CustomerOptions: [
        {
          label: "Add New Customer",
          value: "create_new_customer",
        },
      ],
      leavingfromOptions:[],
      currentItinerary: {
        id: null,
        package_name: "",
        customer_id: "",
        leaving_from_id: null,
        nationality_id: null,
        leaving_on: "",
        number_of_rooms: 1,
        number_of_adults: 1,
        number_of_children: 0,
        company_id: null,
        is_final: false,
        interests: "",
        who_is_travelling: "",
        pregnant_women: false,
        elderly_people: false,
        with_walking_difficulty: false,
        teenager: false,
        women_only: false,
        men_only: false,
        star_rating: 3,
        add_transfers: false,
        destinations: [
          {
            row_id: 1,
            city: { id: null, name: "" },
            nights: 1,
          },
        ],
        add_tours_and_travels: false,
        status: "pending",
      },
      isModelOpen: false,
      sortColumn: "id",
      sortDirection: "asc",
     
      nationalities: [],
    });
    this.onSort = this.onSort.bind(this); // Add this line
    this.openCreateForm = this.openCreateForm.bind(this); // Add this line
    this.closeForm = this.closeForm.bind(this); // Add this line
    this.saveItinerary = this.saveItinerary.bind(this); // Add this line
    this.fetchItineraries = this.fetchItineraries.bind(this); // Add this line
    //   this.handleCustomerChange = this.handleCustomerChange.bind(this);
    this.handleButtonClick = this.handleButtonClick.bind(this);
    this.addDestination = this.addDestination.bind(this);
    this.onChangeCityInput = this.onChangeCityInput.bind(this);
    this.onClickCitySelect = this.onClickCitySelect.bind(this);
    this.onChangeCustomerInput = this.onChangeCustomerInput.bind(this);
    this.onClickCustomerSelect = this.onClickCustomerSelect.bind(this);
    this.onClickLeavingfromSelect = this.onClickLeavingfromSelect.bind(this);
    this.onChangeLeavingfromInput = this.onChangeLeavingfromInput.bind(this);
    this.deleteDestination = this.deleteDestination.bind(this);

    onWillStart(async () => {
      await this.fetchItineraries();
    });
    onMounted(async () => {
      this.handleButtonClick();
    });
  }
  async onChangeLeavingfromInput(e){
    const value = e.target.value;

    console.log("onFocusInput", this.state.isDropdownVisible);

    // Fetch all city options based on the input value
    const cities = await this.orm.searchRead(
      "city.model",
      [["name", "ilike", value]],
      ["name", "id"],
      { limit: 10 }
    );
    
    const availableOptions = cities
    .map((city) => ({ label: city.name, value: city.id }));
    this.state.leavingfromOptions=availableOptions
  }
  async onClickLeavingfromSelect(val){
    console.log("leaving from===>",val);
    this.state.currentItinerary.leaving_from_id=val.value
    console.log(this.state.currentItinerary.leaving_from_id);
    
  }
  async onChangeCustomerInput(e) {
    const value = e.target.value;

    // Fetch all city options based on the input value
    const customer = await this.orm.searchRead(
      "travel.customers",
      [["name", "ilike", value]],
      ["name", "id"],
      { limit: 10 }
    );
    const customeroptions = customer.map((ele, i) => {
      return { label: ele.name, value: ele.id, index: i };
    });
    this.state.CustomerOptions = customeroptions;
  }
  async onClickCustomerSelect(val) {
    console.log(val);
    this.state.currentItinerary.customer_id=val.value
  }
  async fetchItineraries() {
    this.state.data = await this.orm.searchRead(
      "travel.itinerary",
      [],
      ["package_name", "leaving_on", "customer_id", "status", "customer_name"]
    );
    console.log(this.state.data);
  }
  addDestination() {
    // Check if all existing destinations have city values set
    const isValid = this.state.currentItinerary.destinations.every(
      (destination) => destination.city && destination.city.name.trim() !== ""
    );

    if (!isValid) {
      this.notification.add(
        "Please set the city value for all destinations before adding a new one.",
        { type: "warning" }
      );
      // Show an error message or handle the validation failure
      console.error(
        "Please set the city value for all destinations before adding a new one."
      );
      return; // Exit the function to prevent adding a new destination
    }

    // Find the highest current row_id
    const maxRowId = this.state.currentItinerary.destinations.reduce(
      (max, destination) => Math.max(max, destination.row_id),
      0
    );

    // Add a new destination with the incremented row_id
    this.state.currentItinerary.destinations.push({
      row_id: maxRowId + 1, // Increment the highest row_id
      city: { id: null, name: "" },
      nights: 1,
      id:null,
    });
  }

  async onChangeCityInput(e) {
    const value = e.target.value;

    console.log("onFocusInput", this.state.isDropdownVisible);

    // Fetch all city options based on the input value
    const cities = await this.orm.searchRead(
      "city.model",
      [["name", "ilike", value]],
      ["name", "id"],
      { limit: 10 }
    );

    // Get IDs of already selected cities
    const selectedCityIds = this.state.currentItinerary.destinations
      .map((dest) => dest.city.id)
      .filter((id) => id !== null); // Exclude null IDs if any

    // Filter out already selected cities from the options
    const availableOptions = cities
      .filter((city) => !selectedCityIds.includes(city.id))
      .map((city) => ({ label: city.name, value: city.id }));

    // Update state options
    this.state.Options = availableOptions;
  }
  onClickCitySelect(val, row_id) {
    const destination = this.state.currentItinerary.destinations.find(
      (dest) => dest.row_id === row_id
    );
    if (destination) {
      destination.city.id = val.value;
      destination.city.name = val.label;
    }
    console.log(this.state.currentItinerary.destinations);
    this.state.Options = this.state.Options.filter(
      (option) => option.value !== val.value
    );
  }

  async openCreateForm() {
    // this.action.doAction({
    //     type: 'ir.actions.act_window',
    //     name:'Add Itinerary Package',
    //     res_model: 'travel.itinerary',
    //     view_mode: 'form',
    //     views: [[false, 'form']],
    //     target: 'new',
    //     context: {},
    // })

    this.state.cities = await this.orm.searchRead("city.model", [], ["name"], {
      limit: 10,
    });
    // console.log(this.state.cities);
    const customer = await this.orm.searchRead(
      "travel.customers",
      [],
      ["name"]
    );
   
    if (customer.length > 0) {
      const customeroptions = customer.map((ele, i) => {
        return { label: ele.name, value: ele.id, index: i };
      });
      this.state.CustomerOptions = customeroptions;
      console.log(customeroptions, this.state.CustomerOptions);
    }
    this.state.Options = this.state.cities.map((ele) => {
      return { label: ele.name, value: ele.id };
    });
    this.state.leavingfromOptions = this.state.cities.map((ele) => {
      return { label: ele.name, value: ele.id };
    });
    this.state.isModelOpen = true;
    //    // Fetch customers, cities, and countries for dropdowns
       this.state.nationalities = await this.orm.searchRead('country.model', [], ['nationality']);
  }

 
  closeForm() {
    this.state.isModelOpen = false;
  }
 
  onSort(columnKey) {
    console.log(columnKey);
    if (this.state.sortColumn === columnKey) {
      // Toggle sort direction
      this.state.sortDirection =
        this.state.sortDirection === "asc" ? "desc" : "asc";
    } else {
      // Set new sort column and default to ascending direction
      this.state.sortColumn = columnKey;
      this.state.sortDirection = "asc";
    }
    console.log(this.state.sortDirection, this.state.sortColumn);
  }

  handleButtonClick() {
    // Delegate the click handling to the component level for dynamic content
    document.querySelector(".main-table").addEventListener("click", (event) => {
      const action = event.target.closest("button")?.dataset.action;
      const id = event.target.closest("button")?.dataset.id;
      if (action && id) {
        if (action === "edit") {
          console.log("Edit");
          this.action.doAction({
            name: "Edit Itinerary",
            type: "ir.actions.client",
            tag: "edit_itinerary",
            target: "self",
            params: {
              itinerary_id: id,
            },
          });
          // window.location.hash = `#itinerary_id=${id}`;

          //    this.action.doAction(
          //     {

          //         type: 'ir.actions.act_url',
          //         target:'self',
          //         url:`/web#action=edit_itinerary&itinerary_id=${id}`,
          //         params: {
          //             itinerary_id: id, // Pass the itinerary ID
          //         },
          // });
          //    this.action.doAction(
          //     {
          //         type: 'ir.actions.client',
          //         tag: 'edit_itinerary',
          //         target:'self',
          //         params: {
          //             itinerary_id: id, // Pass the itinerary ID
          //         },
          // });
        } else if (action === "delete") {
          console.log("Delete");
          this.dialog.add(ConfirmationDialog, {
            title: "Confirm Delete",
            body: "Are you sure you want to delete this item?",
            confirmClass: "btn btn-danger",
            confirmLabel: "Delete",
            confirm: async () => {
              await this.deleteItinerary(id);
            },
            cancelLabel: "Cancel",
            cancel: () => {},
          });
        }
      }
    });
  }

  async deleteItinerary(id) {
    try {
      console.log(id);

      // Call the Odoo server to delete the record
      await this.orm.call(
        "travel.itinerary", // Model name
        "unlink", // Method name
        [[id]] // Arguments (list of IDs)
      );
      // Show a success notification
      this.notification.add("Itinerary deleted successfully.", {
        type: "success",
      });
      this.fetchItineraries();
    } catch (error) {
      // Handle any errors that occur during the deletion
      console.error("Error deleting itinerary:", error);
      this.notification.add("Failed to delete itinerary.", {
        type: "danger",
      });
    }
  }

  deleteDestination(row_id) {
    console.log("deleteDestination===>", row_id);
    this.state.currentItinerary.destinations = this.state.currentItinerary.destinations.filter(destination => destination.row_id !== row_id);
}
  async saveItinerary() {
    try {
      // Define the model and method
     
      // Prepare the data
      const data = {
        package_name: this.state.currentItinerary.package_name || 'Default Package Name',
        customer_id: parseInt(this.state.currentItinerary.customer_id) || null,  // Ensures it's an integer
        leaving_from_id: parseInt(this.state.currentItinerary.leaving_from_id) || null,
        nationality_id: parseInt(this.state.currentItinerary.nationality_id) || null,
        leaving_on: this.state.currentItinerary.leaving_on || '',  // Ensure a valid datetime string
        number_of_rooms: parseInt(this.state.currentItinerary.number_of_rooms) || 1,
        number_of_adults: parseInt(this.state.currentItinerary.number_of_adults) || 1,
        number_of_children: parseInt(this.state.currentItinerary.number_of_children) || 0,
        interests: this.state.currentItinerary.interests || '',  // Ensure a valid selection value
        who_is_travelling: this.state.currentItinerary.who_is_travelling || '',  // Ensure a valid selection value
        pregnant_women: !!this.state.currentItinerary.pregnant_women,  // Convert to boolean
        elderly_people: !!this.state.currentItinerary.elderly_people,  // Convert to boolean
        with_walking_difficulty: !!this.state.currentItinerary.with_walking_difficulty,  // Convert to boolean
        teenager: !!this.state.currentItinerary.teenager,  // Convert to boolean
        women_only: !!this.state.currentItinerary.women_only,  // Convert to boolean
        men_only: !!this.state.currentItinerary.men_only,  // Convert to boolean
        star_rating: parseInt(this.state.currentItinerary.star_rating) || 3,  // Default to 3 stars if undefined
        add_transfers: !!this.state.currentItinerary.add_transfers,  // Convert to boolean
        add_tours_and_travels: !!this.state.currentItinerary.add_tours_and_travels,  // Convert to boolean
        status: this.state.currentItinerary.status || 'pending',  // Default to 'pending' if undefined
        citynight_ids: this.state.currentItinerary.destinations.map(dest => {
            return  [0, 0, {
                      city_id: dest.city.id,
                      sequence:dest.row_id,
                      nights: parseInt(dest.nights) || 1
                  }];
        })
    };
    
    console.log(data);
      // Validation
    if (!data.customer_id) {
        this.notification.add("Customer is required.",{type:'warning'})
        return
     
        // throw new Error("Customer ID is required.");
    }
    if (!data.leaving_from_id) {
        this.notification.add("Leaving From is required.",{type:'warning'})
        return

        // throw new Error("Leaving From ID is required.");
    }
    if (!data.leaving_on) {
        this.notification.add("Leaving On date is required.",{type:'warning'})
        return
        // throw new Error("Leaving On date is required.");
    }
    const isValid = this.state.currentItinerary.destinations.every(
        (destination) => destination.city && destination.city.name.trim() !== ""
      );
  
      if (!isValid) {
        this.notification.add(
          "Please set the city value for all destinations before adding a new one.",
          { type: "warning" }
        );
        return
    }
    await this.orm.create('travel.itinerary',[data])
     
    //   // Close the form and refresh the data
      this.closeForm();
      this.fetchItineraries(); // You might need to implement this method to refresh the list
    } catch (error) {
      console.error("Error saving itinerary:", error);
    }
  }
}
Itineraries.components = { DataGridComponent, AutoComplete }; // Declare DataGridComponent here

Itineraries.template = "travel_itinerary_template";
registry.category("actions").add("travel_itinerary", Itineraries);
