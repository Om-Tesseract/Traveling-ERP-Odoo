/** @odoo-module **/
import { registry } from "@web/core/registry";
import {
  Component,
  onWillStart,
  onWillUpdateProps,
  useState,
  markup,
} from "@odoo/owl";
import { DataGridComponent } from "../../components/table/datagrid";
import { useService } from "@web/core/utils/hooks";
import { AutoComplete } from "../../components/autocomplete/autocomplete";

import { FormViewDialog } from "@web/views/view_dialogs/form_view_dialog";

export class EditItineraries extends Component {
  setup() {
    super.setup();
    this.orm = useService("orm");
    this.action = useService("action");
    this.notification = useService("notification");

    this.rpc = useService("rpc");
    this.allhotels = useState([]);
    this.activities = useState([]);
    this.selected_itinerary = useState({});
    this.selectedActivity = useState([]);
    this.selectedRTO= useState({});
    this.hotel = useState({});
    this.activity = useState({});
    this.current_hotel_detail = useState({});
    this.state = useState({
      current_step: 1,
      road_transport_options: [],
      cities:[],
      current_hotel_detail_id: null,
      isModelOpen: false,
      Options: [],
      CustomerOptions: [
        {
          label: "Add New Customer",
          value: "create_new_customer",
        },
      ],
      leavingfromOptions:[],
      nationalities: [],
      
      isHotelModelOpen: false,
      isEditActivityModelOpen: false,
      isChangeActivityModelOpen: false,
      isHotelSelectModelOpen: false,
      itinerary: {
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
        add_tours_and_travels: false,
        status: "pending",
        city_nights: [],
        destinations:[],
        delete_citynight:[]
      },
    });
    this.id = this.props.action.params.itinerary_id;

    console.log(this.props.action);
    const params = this.props.action.params; // Retrieve the itinerary ID passed from the action
    onWillStart(async () => {
      await this.loadItinerary(this.id);

      if (params?.itinerary_id) {
        await this.loadItinerary(parseInt(params.itinerary_id));
      }
    });
    this.loadItinerary = this.loadItinerary.bind(this);
    this.edit_action = this.edit_action.bind(this);
    this.set_step = this.set_step.bind(this);
    this.previous_step = this.previous_step.bind(this);
    this.next_step = this.next_step.bind(this);
    this.openHotelModel = this.openHotelModel.bind(this);
    this.closeHotelModel = this.closeHotelModel.bind(this);
    this.closeSeleteHotelModel = this.closeSeleteHotelModel.bind(this);
    this.openSelectHotelModel = this.openSelectHotelModel.bind(this);
    this.updateRoom = this.updateRoom.bind(this);
    this.closeEditActivity = this.closeEditActivity.bind(this);
    this.openEditActivity = this.openEditActivity.bind(this);
    this.saveActivity = this.saveActivity.bind(this);
    this.openChangeActivity = this.openChangeActivity.bind(this);
    this.closeChangeActivity = this.closeChangeActivity.bind(this);
    this.onSelectedActivity = this.onSelectedActivity.bind(this);
    this.saveChangeActivity = this.saveChangeActivity.bind(this);
    this.onSubmitRT = this.onSubmitRT.bind(this);
    this.closeForm = this.closeForm.bind(this); // Add this line

    this.addDestination = this.addDestination.bind(this);
    this.onChangeCityInput = this.onChangeCityInput.bind(this);
    this.onClickCitySelect = this.onClickCitySelect.bind(this);
    this.onChangeCustomerInput = this.onChangeCustomerInput.bind(this);
    this.onClickCustomerSelect = this.onClickCustomerSelect.bind(this);
    this.onClickLeavingfromSelect = this.onClickLeavingfromSelect.bind(this);
    this.onChangeLeavingfromInput = this.onChangeLeavingfromInput.bind(this);
    this.saveItinerary =this.saveItinerary.bind(this);
  }
  addDestination() {
    // Check if all existing destinations have city values set
    const isValid = this.state.itinerary.destinations.every(
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
      return false; // Exit the function to prevent adding a new destination
    }

    // Find the highest current row_id
    const maxRowId = this.state.itinerary.destinations.reduce(
      (max, destination) => Math.max(max, destination.row_id),
      0
    );

    // Add a new destination with the incremented row_id
    this.state.itinerary.destinations.push({
      row_id: maxRowId + 1, // Increment the highest row_id
      city: { id: null, name: "" },
      nights: 1,
      id:null
    });

  }

  async onChangeLeavingfromInput(e){
    const value = e.target.value;

    console.log("onFocusInput");

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
    this.state.itinerary.leaving_from_id=val.value
    console.log(this.state.itinerary.leaving_from_id);
    
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
    this.state.itinerary.customer_id=val.value
  }
  async onChangeCityInput(e) {
    const value = e.target.value;

    console.log("onFocusInput", value);

    // Fetch all city options based on the input value
    const cities = await this.orm.searchRead(
      "city.model",
      [["name", "ilike", value]],
      ["name", "id"],
      { limit: 10 }
    );

    // Get IDs of already selected cities
    const selectedCityIds = this.state.itinerary.destinations
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

    const destination = this.state.itinerary.destinations.find(
      (dest) => dest.row_id === row_id
    );
    console.log(destination,row_id,val);
    
    if (destination) {
      destination.city.id = val.value;
      destination.city.name = val.label;
    }
    console.log("========select=======",this.state.itinerary.destinations);
    this.state.Options = this.state.Options.filter(
      (option) => option.value !== val.value
    );
  }
  async loadItinerary(id) {
    try {
      const rto = await this.orm.searchRead(
        "travel.road.transport.option",
        [],
        []
      );
      const cities = await this.orm.searchRead(
        "city.model",
        [],
        []
      );
      console.log(cities);
      this.state.cities = cities;
      
      const response = await this.rpc("/travels_erp/get_itinerary", {
        itinerary_id: id,
      });
      
      console.log(rto);
      this.state.road_transport_options = rto;
      
      if (response.success) {
        const itinerary = response.itinerary;
        console.log(itinerary);
        const destination= itinerary.city_nights.map((data,i)=>{
          return {
            row_id:i+1,
            city:{id:data.city_id,name:data.city_name},
            nights:data.nights,
            id:data.id
          }
        })
        this.state.itinerary = itinerary;
        this.state.itinerary.destinations=destination
        this.selectedRTO = itinerary.transport_details.length > 0 ? itinerary.transport_details[0] : {
          road_transport_id: null,
          pickup_from_id: null,
          destination_id: null
      };
        console.log("=========",this.selectedRTO );
        
      } else {
        console.error("Failed to load itinerary:", response.message);
      }
    } catch (error) {
      console.error("Error while loading itinerary:", error);
    }
    // try {
    //   // Ensure the ID is in an array
    //   const itinerary = await this.orm.read("travel.itinerary", [id], []);
    //   this.state.currentItinerary=itinerary[0]
    //   const citynights= await this.orm.searchRead("travel.city.night",  [['itinerary_id', '=', id]])
    //     citynights.foreach((ele)=>{
    //         const city_id= ele.city_id[0]
    //          this.orm.read('city.model',[['id','=',city_id]])
    //     })
    // } catch (error) {
    //   console.error("Error loading itinerary:", error);
    // }
  }
  async edit_action() {
    // this.action.doAction({
    //   type: "ir.actions.act_window",
    //   name: "Edit Itinerary Package",
    //   res_model: "travel.itinerary",
    //   view_mode: "form",
    //   views: [[false, "form"]],
    //   target: "new",
    //   res_id: 2,
    //   context: {},
    // });
    const cities = await this.orm.searchRead("city.model", [], ["name"], {
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
    this.state.Options =cities.map((ele) => {
      return { label: ele.name, value: ele.id };
    });
    this.state.leavingfromOptions = this.state.cities.map((ele) => {
      return { label: ele.name, value: ele.id };
    });
    this.state.isModelOpen = true;
    //    // Fetch customers, cities, and countries for dropdowns
    this.state.nationalities = await this.orm.searchRead('country.model', [], ['nationality']);
    
    this.state.isModelOpen = true;

  }
  set_step(step) {
    this.state.current_step = step;
    this.render();
  }

  previous_step() {
    if (this.state.current_step > 1) {
      this.state.current_step--;
      this.render();
    }
  }

  next_step() {
    if (this.state.current_step < 4) {
      this.state.current_step++;
      this.render();
    }
  }
  async openHotelModel(city_id, hotel_detail_id) {
    console.log("=======", city_id);
    if (hotel_detail_id) {
      this.state.current_hotel_detail_id = hotel_detail_id;
    }
    try {
      const response = await this.rpc("/travels_erp/all_hotels", {
        city_id: city_id,
      });
      console.log(response);
      this.allhotels = response;
    } catch (error) {
      console.error("Error while loading itinerary:", error);
    }
    this.state.isHotelModelOpen = true;
  }
  async saveItinerary() {
    try {
        // Prepare the data
        const data = {
            package_name: this.state.itinerary.package_name || 'Default Package Name',
            customer_id: parseInt(this.state.itinerary.customer_id) || null,
            leaving_from_id: parseInt(this.state.itinerary.leaving_from_id) || null,
            nationality_id: parseInt(this.state.itinerary.nationality_id) || null,
            leaving_on: this.state.itinerary.leaving_on || '',
            number_of_rooms: parseInt(this.state.itinerary.number_of_rooms) || 1,
            number_of_adults: parseInt(this.state.itinerary.number_of_adults) || 1,
            number_of_children: parseInt(this.state.itinerary.number_of_children) || 0,
            interests: this.state.itinerary.interests || '',
            who_is_travelling: this.state.itinerary.who_is_travelling || '',
            pregnant_women: !!this.state.itinerary.pregnant_women,
            elderly_people: !!this.state.itinerary.elderly_people,
            with_walking_difficulty: !!this.state.itinerary.with_walking_difficulty,
            teenager: !!this.state.itinerary.teenager,
            women_only: !!this.state.itinerary.women_only,
            men_only: !!this.state.itinerary.men_only,
            star_rating: parseInt(this.state.itinerary.star_rating) || 3,
            add_transfers: !!this.state.itinerary.add_transfers,
            add_tours_and_travels: !!this.state.itinerary.add_tours_and_travels,
            status: this.state.itinerary.status || 'pending',
            citynight_ids: this.state.itinerary.destinations.map(dest => {
                if (dest.id) {
                    return [1, dest.id, {
                        city_id: dest.city.id,
                        sequence: dest.row_id,
                        nights: parseInt(dest.nights) || 1
                    }];
                } else {
                    return [0, 0, {
                        city_id: dest.city.id,
                        sequence: dest.row_id,
                        nights: parseInt(dest.nights) || 1
                    }];
                }
            })
        };

        console.log("Final data to be saved:", data);

        // Perform validation checks
        if (!data.customer_id || !data.leaving_from_id || !data.leaving_on) {
            this.notification.add("Required fields are missing.", { type: 'warning' });
            return;
        }

        const isValid = this.state.itinerary.destinations.every(
            (destination) => destination.city && destination.city.name.trim() !== ""
        );

        if (!isValid) {
            this.notification.add(
                "Please set the city value for all destinations before adding a new one.",
                { type: "warning" }
            );
            return;
        }

        await this.orm.write('travel.itinerary', [parseInt(this.id)], data);

        this.closeForm();
        this.loadItinerary(this.id);

    } catch (error) {
        console.error("Error saving itinerary:", error);
        this.notification.add(`Error saving itinerary: ${error.message}`, { type: 'danger' });
    }
}

    closeHotelModel() {
    this.state.isHotelModelOpen = false;
  }
  closeForm() {
    this.state.isModelOpen = false;
  }
  async onSubmitRT() {
    try {
        // Ensure `selectedRTO` has updated values from the form
        const updatedDetails = {
            road_transport_id: parseInt(this.selectedRTO.road_transport_id),
            pickup_from_id: parseInt(this.selectedRTO.pickup_from_id),
            destination_id: parseInt(this.selectedRTO.destination_id),
            // Include other fields as necessary
        };

        // Send updated details to the server or process them as needed
        const response = await this.orm.write("travel.road.transport.details",[this.selectedRTO.id], updatedDetails);

            this.notification.add('Successfully updated transport details.', {'type': 'success'});
            // Optionally refresh or update the UI as needed
      this.render()
    } catch (error) {
        console.error("Error while updating transport details:", error);
        this.notification.add('An error occurred while updating transport details.', {'type':'danger'});
    }
}


  async closeEditActivity() {
    this.state.isEditActivityModelOpen = false;
  }
  async openEditActivity(act) {
    this.activity = act;
    this.state.isEditActivityModelOpen = true;
  }
  async closeChangeActivity() {
    this.state.isChangeActivityModelOpen = false;
  }
  async openChangeActivity(itiner, city_id) {
    console.log(itiner, city_id);
    try {
      const res = await this.orm.searchRead("travel.activity", [
        ["activity_city_id", "=", city_id],
      ]);
      console.log(res);
      this.selected_itinerary=itiner
      this.selectedActivity = [...itiner.activity];
      this.activities = res;
      this.state.isChangeActivityModelOpen = true;
    } catch (error) {
      console.error("Error fetching activities:", error);
    }
  }
  async onSelectedActivity(act) {
    if (!this.selectedActivity) {
        this.selectedActivity = [];
    }
    delete act.id

    this.selectedActivity = [...this.selectedActivity,act];

    console.log("=============>",this.selectedActivity);

    this.render();
 
}

  async openSelectHotelModel(hotel_id, hotel_detail_id) {
    console.log("=======>", hotel_id);
    if (hotel_detail_id) {
      this.state.current_hotel_detail_id = hotel_detail_id;
    }
    try {
      const response = await this.rpc("/travels_erp/hotel", {
        hotel_id: hotel_id,
      });
      const result = await this.orm.read(
        "travel.hotel.details",
        [hotel_detail_id],
        []
      );
      this.current_hotel_detail = result[0];
      console.log(result);

      console.log(response);
      this.hotel = response;
    } catch (error) {
      console.error("Error while loading hotel:", error);
    }
    this.state.isHotelSelectModelOpen = true;
  }
  closeSeleteHotelModel() {
    this.state.isHotelSelectModelOpen = false;
  }
  
  async saveChangeActivity(){
    try {
      console.log(this.selectedActivity);
      const newSelAct = this.selectedActivity
      .filter(element => !element.id)
      .map(element => {
          return {
              activity_desc: element.activity_desc,
              activity_name: element.activity_name,
              age_limit: element.age_limit,
              category: element.category, // This should match the many2many field's format
              duration: element.duration,
              itinerary_id: this.selected_itinerary.id,
              activity_city_id: element.activity_city_id[0]
          };
      });
      console.log(newSelAct);
      if (newSelAct.length > 0) {
        // Save the new activities to the database using Odoo ORM service
        const createdActivities = await this.orm.create('travel.itinerary.activity', newSelAct);
        console.log('Created Activities:', createdActivities);
        this.loadItinerary(this.orm)
        this.render();
        
        // Optionally, handle success feedback, such as closing the modal
        this.closeChangeActivity();

    } else {
        console.log('No new activities to save.');
    }
    }
    catch (e) {
      console.error(e);
      
    }
  }
  async saveActivity() {
    try {
      // Access the orm service
      const orm = this.orm;

      // Update the activity record in the Odoo database
      await orm.write("travel.itinerary.activity", [this.activity.id], {
        activity_name: this.activity.activity_name,
        duration: this.activity.duration,
        age_limit: this.activity.age_limit,
        activity_desc: this.activity.activity_desc,
        activity_city_id: this.activity.activity_city_id,
        category: this.activity.category,
        sequence: this.activity.sequence,
      });

      // Close the edit modal after saving
      this.closeEditActivity();
      this.loadItinerary(this.id);
      // Optionally, show a success message or refresh data
      this.notification.add("Activity updated successfully!", {
        type: "success",
      });
    } catch (error) {
      console.error("Error saving activity:", error);
      this.notification.add("Error updating activity.", {
        type: "danger",
      });
    }
  }

  async updateRoom(roomCatId) {
    try {
      // Get selected room
      const selectedRoom = document.querySelector(
        `input[name="selected_room${roomCatId}"]:checked`
      );
      const roomId = selectedRoom ? selectedRoom.value : null;

      // Get selected meal plan
      const mealPlanElement = document.getElementById(`meal_plan_${roomCatId}`);
      const mealPlan = mealPlanElement ? mealPlanElement.value : "";

      // Get additional request
      const additionalRequestElement = document.getElementById(
        `additional_request_${roomCatId}`
      );
      const additionalRequest = additionalRequestElement
        ? additionalRequestElement.value
        : "";

      // Now you have the roomId, mealPlan, and additionalRequest
      console.log(
        "Selected Room ID:",
        this.state.current_hotel_detail_id,
        roomId
      );
      console.log("Selected Meal Plan:", mealPlan);
      console.log("Additional Request:", additionalRequest);

      const updated = await this.orm.write(
        "travel.hotel.details",
        [this.state.current_hotel_detail_id],
        {
          room_id: parseInt(roomId),
          meal_plans: mealPlan,
          category: roomCatId,
          hotel_id: this.hotel.id,
          additional_requests: additionalRequest,
        }
      );
      this.closeSeleteHotelModel();
      this.closeHotelModel();
      this.loadItinerary(this.id);
    } catch (error) {
      console.error("Error while updating room:", error);
    }
  }
}

EditItineraries.components = { DataGridComponent,AutoComplete }; // Declare DataGridComponent here

EditItineraries.template = "travel_edit_itinerary_template";
registry.category("actions").add("edit_itinerary", EditItineraries);
