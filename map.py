import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QFrame,
    QSpacerItem,
    QSizePolicy,
    QComboBox,
    QMessageBox,
    QCheckBox,
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
import folium
import flight_graph
from utils.calculation_utils import format_duration
import re
import folium.plugins


class MapWindow(QMainWindow):

    def __init__(self):

        super().__init__()
        self.AirportGraph = flight_graph.FlightGraph(
            "data/europe_airports.csv", "data/europe_flight_dataset.csv"
        )
        self.setWindowTitle("Airport Locator")
        self.setGeometry(100, 100, 1920, 1080)

        # Data for countries
        self.country_data = self.AirportGraph.group_airports_by_country()

        # Data for dropdowns
        self.source_airport_data = []
        self.destination_airport_data = []

        # Data for maximum flights
        self.nums_of_flight_added = 0
        self.max_no_of_flight = 2

        # List to store newly added flight field layouts
        self.flight_fields = []

        # Create input field and button
        self.source_country_input_label = QLabel("Source Country:")
        self.source_airport_input_label = QLabel("Source Airport:")
        self.destination_country_input_label = QLabel("Destination Country:")
        self.destination_airport_input_label = QLabel("Destination Airport:")

        # Dropdown for Source Country
        self.source_country_dropdown = QComboBox(self)
        self.source_country_dropdown.setFixedWidth(200)
        self.source_country_dropdown.addItems(self.country_data.keys())
        self.source_country_dropdown.setEditable(True)
        self.source_country_dropdown.setCurrentIndex(-1)
        self.source_country_dropdown.currentIndexChanged.connect(
            self.update_source_airport_dropdown
        )

        # Dropdown for Source States
        self.source_airport_dropdown = QComboBox(self)
        self.source_airport_dropdown.setFixedWidth(200)
        self.source_airport_dropdown.setEditable(True)

        # Dropdown for Destination Country
        self.destination_country_dropdown = QComboBox(self)
        self.destination_country_dropdown.setFixedWidth(200)
        self.destination_country_dropdown.addItems(self.country_data.keys())
        self.destination_country_dropdown.setEditable(True)
        self.destination_country_dropdown.setCurrentIndex(-1)
        self.destination_country_dropdown.currentIndexChanged.connect(
            self.update_destination_airport_dropdown
        )

        # Dropdown for Destination States
        self.destination_airport_dropdown = QComboBox(self)
        self.destination_airport_dropdown.setFixedWidth(200)
        self.destination_airport_dropdown.setEditable(True)

        # Create layout for source_country
        source_country_layout = QHBoxLayout()
        source_country_layout.addWidget(self.source_country_input_label)
        source_country_layout.addWidget(self.source_country_dropdown)
        source_country_layout.setAlignment(Qt.AlignHCenter)

        # Create layout for source_state
        source_airport_layout = QHBoxLayout()
        source_airport_layout.addWidget(self.source_airport_input_label)
        source_airport_layout.addWidget(self.source_airport_dropdown)
        source_airport_layout.setAlignment(Qt.AlignHCenter)

        # Create layout to contain source
        source_container = QVBoxLayout()
        source_container.addLayout(source_country_layout)
        source_container.addLayout(source_airport_layout)
        source_container.setContentsMargins(0, 0, 0, 15)

        # Create layout for destination_country
        destination_country_layout = QHBoxLayout()
        destination_country_layout.addWidget(self.destination_country_input_label)
        destination_country_layout.addWidget(self.destination_country_dropdown)
        destination_country_layout.setAlignment(Qt.AlignHCenter)

        # Create layout for source_state
        destination_airport_layout = QHBoxLayout()
        destination_airport_layout.addWidget(self.destination_airport_input_label)
        destination_airport_layout.addWidget(self.destination_airport_dropdown)
        destination_airport_layout.setAlignment(Qt.AlignHCenter)

        # Create layout to contain destination
        destination_container = QVBoxLayout()
        destination_container.addLayout(destination_country_layout)
        destination_container.addLayout(destination_airport_layout)

        # Create Checkbox for choosing airports

        self.optimal_checkbox = QCheckBox("Optimal Path")
        self.shortest_dist_checkbox = QCheckBox("Shortest Distance")
        self.cheapest_checkbox = QCheckBox("Cheapest Cost")
        self.shortest_dur_checkbox = QCheckBox("Shortest Duration")
        self.least_layover_checkbox = QCheckBox("Least Layover")

        # Create layout for checkboxes
        checkbox_layout = QVBoxLayout()
        checkbox_layout.addWidget(self.optimal_checkbox)  # optimal
        checkbox_layout.addSpacing(10)
        checkbox_layout.addWidget(self.shortest_dist_checkbox)  # shortest distance
        checkbox_layout.addSpacing(10)
        checkbox_layout.addWidget(self.cheapest_checkbox)  # least cost
        checkbox_layout.addSpacing(10)
        checkbox_layout.addWidget(self.shortest_dur_checkbox)  # shortest duration
        checkbox_layout.addSpacing(10)
        checkbox_layout.addWidget(self.least_layover_checkbox)  # least layover
        checkbox_layout.setAlignment(Qt.AlignHCenter)
        checkbox_layout.setContentsMargins(0, 20, 0, 20)

        # Create button to search airports
        self.search_button = QPushButton("Search")
        self.search_button.setFixedSize(120, 40)
        self.search_button.clicked.connect(self.show_airport_on_map)

        # Create button to add airports for multicity
        self.add_button = QPushButton("Add Flight")
        self.add_button.setFixedSize(120, 40)
        self.add_button.clicked.connect(lambda: self.add_flight_fields(input_layout))

        self.remove_button = QPushButton("Remove Last Flight")
        self.remove_button.setFixedSize(120, 40)
        self.remove_button.clicked.connect(
            lambda: self.remove_last_flight(input_layout)
        )

        search_button_layout = QHBoxLayout()
        search_button_layout.addWidget(self.remove_button)
        search_button_layout.addSpacing(10)
        search_button_layout.addWidget(self.add_button)
        search_button_layout.addSpacing(10)
        search_button_layout.addWidget(self.search_button)
        search_button_layout.setAlignment(Qt.AlignHCenter)

        # Create layout for inputs
        input_layout = QVBoxLayout()
        input_layout.addLayout(source_container)
        input_layout.addLayout(destination_container)
        input_layout.addLayout(checkbox_layout)
        input_layout.addLayout(search_button_layout)
        input_layout.setContentsMargins(0, 120, 0, 0)
        input_layout.addStretch()
        input_layout.setSpacing(0)

        # Frame to contain entire input section
        input_frame = QFrame()
        input_frame.setLayout(input_layout)

        # Create Folium map
        self.map = folium.Map(
            location=(50.170824, 15.087472), zoom_start=4, tiles="cartodb positron"
        )
        self.map.save("map.html")

        # Create WebEngineView to display the map

        self.web_view = QWebEngineView()
        self.web_view.setHtml(open("map.html").read())  # Load the HTML file

        # Create layout for map
        map_layout = QVBoxLayout()
        map_layout.addWidget(self.web_view)

        # Create frame for map
        map_frame = QFrame()
        map_frame.setLayout(map_layout)

        # Create main layout to hold components
        main_layout = QHBoxLayout()
        main_layout.addWidget(input_frame, 1)
        main_layout.addWidget(map_frame, 3)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def add_flight_fields(self, input_layout):
        """
            Adds up to two multi-country fields to enable multi-flights

            Args:
                input_layout (object): Layout of the entire selection field

        """
        # Create input fields for new flight
        field_counter = len(self.flight_fields) + 1

        new_destination_country_label = QLabel(f"Stop {field_counter} Country:")
        new_destination_airport_label = QLabel(f"Stop {field_counter} Airport:")

        new_destination_country_dropdown = QComboBox(self)
        new_destination_country_dropdown.setFixedWidth(200)
        new_destination_country_dropdown.addItems(self.country_data.keys())
        new_destination_country_dropdown.setEditable(True)
        new_destination_country_dropdown.setCurrentIndex(-1)

        new_destination_airport_dropdown = QComboBox(self)
        new_destination_airport_dropdown.setFixedWidth(200)
        new_destination_airport_dropdown.setEditable(True)

        new_destination_country_dropdown.currentIndexChanged.connect(
            lambda: self.update_new_destination_dropdown(
                new_destination_country_dropdown, new_destination_airport_dropdown
            )
        )

        # Create layouts for new flight fields

        new_destination_country_layout = QHBoxLayout()
        new_destination_country_layout.addWidget(new_destination_country_label)
        new_destination_country_layout.addWidget(new_destination_country_dropdown)
        new_destination_country_layout.setAlignment(Qt.AlignHCenter)

        new_destination_airport_layout = QHBoxLayout()
        new_destination_airport_layout.addWidget(new_destination_airport_label)
        new_destination_airport_layout.addWidget(new_destination_airport_dropdown)
        new_destination_airport_layout.setAlignment(Qt.AlignHCenter)

        new_destination_container = QVBoxLayout()
        new_destination_container.addLayout(new_destination_country_layout)
        new_destination_container.addLayout(new_destination_airport_layout)

        fields_container = QVBoxLayout()

        fields_container.addLayout(new_destination_container)

        new_flight_fields = [fields_container]

        # Check if the number of flights added exceed the max number we allowed
        if self.nums_of_flight_added < self.max_no_of_flight:
            # Add all accumulated layouts at the end of input_layout
            for layout in new_flight_fields:
                input_layout.insertLayout(input_layout.count() - 3, layout)
            # Append layouts to flight_fields list
            self.flight_fields.extend(
                new_flight_fields
            )
            self.nums_of_flight_added += 1
        else:
            QMessageBox.information(
                self,
                "Maximum Limit Reached",
                "You can only add a maximum of 3 source-destination pairs.",
            )

    def remove_last_flight(self, input_layout):
        """
            Removes the airport stops fields

            Args:
                input_layout (object): Layout of the entire selection field

        """
        if self.nums_of_flight_added > 0:
            # Get the item representing the last flight field layout
            layout_to_remove = input_layout.itemAt(input_layout.count() - 4)

            # Remove the layout from the input_layout
            input_layout.removeItem(layout_to_remove)

            # Clear widgets within the removed layout efficiently
            self.clear_layout(layout_to_remove)

            # Update number of flights and remove layout from flight_fields list
            self.nums_of_flight_added -= 1
            del self.flight_fields[-1]

        else:
            QMessageBox.information(
                self, "No Flights to Remove", "There are no flights to remove yet."
            )

    def clear_layout(self, layout):
        """
            Helps to clear away all the widgets inside the layout

            Args:
                layout (object): Layout of the specific field

        """
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(
                        item.layout()
                    )  # Recursive call for nested layouts

    def update_map_view(self):
        self.map_view.reload()

    def update_source_airport_dropdown(self):
        """
            Update the source airport accordingly to the country selected
        """
        selected_country = self.source_country_dropdown.currentText()
        self.source_airport_data = self.country_data.get(selected_country, [])
        self.source_airport_dropdown.clear()
        self.source_airport_dropdown.addItems(self.source_airport_data)

    def update_destination_airport_dropdown(self):
        """
            Update the destination airport accordingly to the country selected
        """
        selected_country = self.destination_country_dropdown.currentText()
        self.destination_airport_data = self.country_data.get(selected_country, [])
        self.destination_airport_dropdown.clear()
        self.destination_airport_dropdown.addItems(self.destination_airport_data)

    def update_new_destination_dropdown(self, dropbox_country, dropbox_airport):
        """
            Update the new stops airport accordingly to the country selected

            Args:
                dropbox_country (QComboBox): dropbox of the country
                dropbox_airport (QComboBox): dropbox of the airports available in the country
        """
        selected_country = dropbox_country.currentText()
        self.destination_airport_data = self.country_data.get(selected_country, [])
        dropbox_airport.clear()
        dropbox_airport.addItems(self.destination_airport_data)

    def get_new_destination_airport_texts(self):

        """
            Gets the current text inside the dropbox for stop country and airport fields
            Returns:
                list: consist of the all the current text from the drop boxes
        """
        new_destination_airport_texts = []
        for flight_layout in self.flight_fields:
            # Check if flight_layout has items (not empty)
            if flight_layout.count() > 0:
                try:
                    # Attempt to access the dropdown widget
                    dropdown_widget = (
                        flight_layout.itemAt(0).itemAt(1).itemAt(1).widget()
                    )

                    new_destination_airport_texts.append(dropdown_widget.currentText())
                except AttributeError:
                    # Handle cases where dropdown widget might not exist
                    print("Dropdown widget not found in a flight layout")
            else:
                # Handle cases where flight_layout is empty
                print("Flight layout is empty")
        return new_destination_airport_texts

    def search_flights(self):
        """
            Using all the dropdown boxes text and finding all the IATA codes that matches the dropdown box text

            Returns:
                list: consist of the all the IATA codes from source, destination, intermediaries airports
        """
        pattern = r"\(([A-Z]{3})\)"

        source_airport = self.source_airport_dropdown.currentText()
        destination_airport = self.destination_airport_dropdown.currentText()

        source_iata, destination_iata = None, None
        source_iata_match = re.search(pattern, source_airport)
        if source_iata_match:
            source_iata = source_iata_match.group(1)
        destination_iata_match = re.search(pattern, destination_airport)
        if destination_iata_match:
            destination_iata = destination_iata_match.group(1)
        source_destination_iata = [source_iata, destination_iata]

        intermediate_airport = self.get_new_destination_airport_texts()
        intermediary_airport_list = []
        for intermediary in intermediate_airport:
            match = re.search(pattern, intermediary)
            if match:
                intermediary_airport_list.append(match.group(1))
        if not intermediary_airport_list:
            intermediary_airport_list = None

        source_destination_iata.append(intermediary_airport_list)

        return source_destination_iata

    def create_paths(self, chosen_path, node_airport, airport_map, destination_iata, color):
        """
            Create the path line for the path created by the algorithm

            Args:
                chosen_path (dict): A dictionary consist of the paths, segments, total stops, total duration and total cost of the source to destination
                node_airport (dict): A dictionary that contains all the airports available
                airport_map (Map): A map using folium
                destination_iata (str): The destination IATA code
                color (str): Color of the path
        """
        edge_coords = []

        path, segment, stop, cost, duration = (
            chosen_path["path"],
            chosen_path["segments"],
            chosen_path["total_stops"],
            chosen_path["total_cost"],
            chosen_path["total_duration"],
        )
        if chosen_path is None:
            QMessageBox.information(
                self, "No Path Found", "No path found between selected airports."
            )
        for i, iata in enumerate(path):
            airport_path = node_airport.get(iata)
            if airport_path:
                text = f"Airport Name: {airport_path.name}({airport_path.iata_code})"
                popup = folium.Popup(text, max_width=250)
                folium.Marker(
                    location=[airport_path.latitude, airport_path.longitude],
                    popup=popup,
                    icon=folium.Icon(color=color),
                ).add_to(airport_map)
                edge_coords.append((airport_path.latitude, airport_path.longitude))
                if i < len(path) - 1:
                    current_airport = node_airport.get(iata)
                    next_airport = node_airport.get(path[i + 1])
                    midpoint = (next_airport.latitude,
                                next_airport.longitude)
                    edge_coords.append(midpoint)

                    segment_info = segment[i]
                    popup_text = f"Distance: {segment_info['distance']:.2f} km<br>Cost: ${segment_info['cost']}<br>Duration: {format_duration(segment_info['duration'])}"
                    folium.plugins.AntPath(
                        locations=edge_coords,
                        tooltip=popup_text,
                        color=color,
                        weight=5.5,
                        opacity=1
                    ).add_to(airport_map)
                    edge_coords = [midpoint]  # Reset edge_coords for the next segment
        # folium.plugins.AntPath(
        #     locations=edge_coords, color=color, weight=2.5, opacity=1
        # ).add_to(airport_map)

        if path[-1] != destination_iata:
            QMessageBox.information(
                self,
                "Rerouting occurred ",
                f"Rerouting occurred to destination {path[-1]} airport, please take note",
            )

    def show_airport_on_map(self):
        """
            Function to check which checkboxes are ticked and show the paths accordingly to what users select.
            Calls self.create_path() to create the necessary paths on the map

            Returns:
                list: consist of the all the IATA codes from source, destination, intermediaries airports
        """
        source_iata, destination_iata, intermediate_iata = self.search_flights()
        # Check if source and destination are different
        if source_iata == destination_iata:
            QMessageBox.information(self, "Invalid Route Path", "Please select two different airports")
            return

        #Check if any options is selected if dont process
        if ((self.optimal_checkbox.isChecked() is False) and (self.cheapest_checkbox.isChecked() is False) and (self.shortest_dur_checkbox.isChecked() is False)
            and (self.least_layover_checkbox.isChecked() is False) and (self.shortest_dist_checkbox.isChecked() is False)):
            QMessageBox.information(self, "Invalid Selection", "Please select one of the categories")
            return    

        locations = [source_iata, destination_iata]

        # Check if intermediate_iata is provided
        if intermediate_iata is not None:
            locations.extend(intermediate_iata)

            # Check if stop 1, stop 2, stop 1 to destination, and stop 2 to destination are the same
            if len(set(locations)) != len(locations):
                QMessageBox.information(self, "Invalid Route Path", "One or more locations are the same")
                return

        airport_graph = self.AirportGraph
        airport_map = folium.Map(
            location=[50.170824, 15.087472], zoom_start=4, tiles="cartodb positron"
        )
        node_airport = airport_graph.airports
        message_information = []

        # Optimal Path
        if self.optimal_checkbox.isChecked():
            optimal_path = airport_graph.find_route(
                source_iata, destination_iata, "optimal", intermediate_iata
            )
            if optimal_path:
                self.create_paths(
                    optimal_path, node_airport, airport_map, destination_iata, "red"
                )
            else:
                message_information.append(f"Optimal: No Flight Routes Available from {source_iata} to {destination_iata}")
    
        # Shortest Distance Path
        if self.shortest_dist_checkbox.isChecked():
            shortest_path = airport_graph.find_route(
                source_iata, destination_iata, "shortest distance", intermediate_iata
            )
            if shortest_path:
                self.create_paths(
                    shortest_path, node_airport, airport_map, destination_iata, "orange"
                )
            else:
                message_information.append(f"Shortest: No Flight Routes Available from {source_iata} to {destination_iata}")
            

        # Cheapest Path
        if self.cheapest_checkbox.isChecked():
            cheapest_path = airport_graph.find_route(
                source_iata, destination_iata, "least cost", intermediate_iata
            )
            if cheapest_path:
                self.create_paths(
                    cheapest_path, node_airport, airport_map, destination_iata, "purple"
                )
            else:
                message_information.append(f"Cheapest: No Flight Routes Available from {source_iata} to {destination_iata}")
            
        # Shortest Duration Path
        if self.shortest_dur_checkbox.isChecked():
            shortest_dur_path = airport_graph.find_route(
                source_iata, destination_iata, "shortest duration", intermediate_iata
            )
            if shortest_dur_path:
                self.create_paths(
                    shortest_dur_path,
                    node_airport,
                    airport_map,
                    destination_iata,
                    "green",
                )
            else:
                message_information.append(f"Shortest Duration: No Flight Routes Available from {source_iata} to {destination_iata}")
            
        # Least Layovers Path
        if self.least_layover_checkbox.isChecked():
            least_layover_path = airport_graph.find_route(
                source_iata, destination_iata, "least layovers", intermediate_iata
            )
            if least_layover_path:
                self.create_paths(
                    least_layover_path,
                    node_airport,
                    airport_map,
                    destination_iata,
                    "blue",
                )
            else:
                message_information.append(f"Least Layover: No Flight Routes Available from {source_iata} to {destination_iata}")

        messageString = ""        
        if message_information is not None:
            for message in message_information:
                messageString += message + "\n"
                
        if messageString != "":
            QMessageBox.information(self,"No Flightes Routes Available",messageString)

        airport_map.save("airport_map.html")
        self.web_view.setHtml(open("airport_map.html").read())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MapWindow()
    window.show()
    sys.exit(app.exec_())
