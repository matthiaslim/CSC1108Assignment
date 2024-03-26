import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, \
    QWidget, QFrame, QSpacerItem, QSizePolicy, QComboBox, QMessageBox, QCheckBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
import folium
import flight_tracker
import re
import folium.plugins


class MapWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.AirportGraph = flight_tracker.FlightGraph("europe_airports.csv", "europe_flight_dataset.csv")
        # print(self.AirportGraph.group_airports_by_country())

        self.setWindowTitle("Airport Locator")
        self.setGeometry(100, 100, 1920, 1080)

        self.country_data = self.AirportGraph.group_airports_by_country()

        # self.checkboxes = {
        #     "BFS Path": QCheckBox("BFS Path"),
        #     "Dijkstra Path": QCheckBox("Dijkstra Path"),
        #     "Third Path": QCheckBox("Third Path")
        # }

        # Data for testing purposes
        # self.country_data = {'Albania': ['Tirana International Airport Mother Teresa (TIA)',
        #                                  'Deft International Airport Mother Teresa (DIA)',
        #                                  'Allah International Airport Mother Teresa (AIA)'],
        #                      'Austria': ['Graz Airport (GRZ)', 'Innsbruck Airport (INN)',
        #                                  'Linz Hörsching Airport (LNZ)', 'Salzburg Airport (SZG)',
        #                                  'Vienna International Airport (VIE)'],
        #                      'Belarus': ['Gomel Airport (GME)', 'Vitebsk Vostochny Airport (VTB)',
        #                                  'Minsk 1 Airport (MHP)', 'Minsk National Airport (MSQ)',
        #                                  'Hrodna Airport (GNA)', 'Mogilev Airport (MVQ)', 'Brest Airport (BQT)']}

        # Data for dropdowns
        self.source_airport_data = []
        self.destination_airport_data = []

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
        self.source_country_dropdown.currentIndexChanged.connect(self.update_source_airport_dropdown)

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
        self.destination_country_dropdown.currentIndexChanged.connect(self.update_destination_airport_dropdown)

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
        source_container.setContentsMargins(0, 0, 0, 40)

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
        self.bfs_checkbox = QCheckBox("Least Layovers")
        self.dijkstra_checkbox = QCheckBox("Fastest Path")
        self.cost_checkbox = QCheckBox("Cheapest Path")
        # self.bfs_checkbox.stateChanged.connect(self.update_displayed_paths)
        # self.dijkstra_checkbox.stateChanged.connect(self.update_displayed_paths)

        # Create layout for checkboxes
        checkbox_layout = QVBoxLayout()
        checkbox_layout.addWidget(self.bfs_checkbox)
        checkbox_layout.addWidget(self.dijkstra_checkbox)
        checkbox_layout.addWidget(self.cost_checkbox)
        checkbox_layout.setAlignment(Qt.AlignHCenter)
        checkbox_layout.setContentsMargins(0, 20, 0, 20)

        # Create button to search airports
        self.search_button = QPushButton("Search")
        self.search_button.setFixedSize(120, 40)
        self.search_button.clicked.connect(self.show_airport_on_map)
        search_button_layout = QVBoxLayout()
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
        self.map = folium.Map(location=(50.170824, 15.087472), zoom_start=4, tiles="cartodb positron")
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

    # def show_airport_location(self):
    #     iata_code = self.input_field.text().strip().upper()  # Get the entered IATA code
    #     # Add marker for the airport location
    #     # Replace the coordinates with the actual coordinates for the IATA code
    #     folium.Marker([0, 0], popup=iata_code).add_to(self.map)
    #     self.map_view = folium.Map().get_root().render()
    #     self.update_map_view()

    def update_map_view(self):
        self.map_view.reload()

    def update_source_airport_dropdown(self):
        selected_country = self.source_country_dropdown.currentText()
        self.source_airport_data = self.country_data.get(selected_country, [])
        self.source_airport_dropdown.clear()
        self.source_airport_dropdown.addItems(self.source_airport_data)

    def update_destination_airport_dropdown(self):
        selected_country = self.destination_country_dropdown.currentText()
        self.destination_airport_data = self.country_data.get(selected_country, [])
        self.destination_airport_dropdown.clear()
        self.destination_airport_dropdown.addItems(self.destination_airport_data)

    def search_flights(self):

        source_airport = self.source_airport_dropdown.currentText()
        destination_airport = self.destination_airport_dropdown.currentText()

        pattern = r'\(([A-Z]{3})\)'
        source_iata, destination_iata = None, None
        source_iata_match = re.search(pattern, source_airport)
        if source_iata_match:
            source_iata = source_iata_match.group(1)
        destination_iata_match = re.search(pattern, destination_airport)
        if destination_iata_match:
            destination_iata = destination_iata_match.group(1)
        source_destination_iata = [source_iata, destination_iata]
        print(source_destination_iata)
        return source_destination_iata

    def show_airport_on_map(self):
        source_iata, destination_iata = self.search_flights()
        airport_graph = self.AirportGraph

        airport_map = folium.Map(location=[50.170824, 15.087472], zoom_start=4, tiles="cartodb positron")
        node_airport = airport_graph.airports

        # For dijkstra_path
        if self.dijkstra_checkbox.isChecked():
            edge_coords = []
            dijkstra_path = airport_graph.find_shortest_path(source_iata, destination_iata)
            if dijkstra_path is None:
                QMessageBox.information(self, "No Path Found", "No path found between selected airports.")
                return
            for iata in dijkstra_path:
                airport_path = node_airport.get(iata)
                if airport_path:
                    text = f"Airport Name :{airport_path.name} Airport Code :{airport_path.iata_code}"
                    folium.Marker(location=[airport_path.latitude, airport_path.longitude], popup=text,
                                  icon=folium.Icon(color="blue")).add_to(airport_map)
                    edge_coords.append((airport_path.latitude, airport_path.longitude))
            folium.plugins.AntPath(locations=edge_coords, color="red", weight=2.5, opacity=1).add_to(airport_map)
            if dijkstra_path[-1] != destination_iata:
                QMessageBox.information(self, "Rerouting occurred ", f"Rerouting occurred to destination {dijkstra_path[-1]} airport, please take note")

        # For BFS
        if self.bfs_checkbox.isChecked():

            bfs_path = airport_graph.least_layovers_bfs(source_iata, destination_iata)
            bfs_coords = []
            bfs_route, no_of_layovers = bfs_path
            if bfs_route is None:
                QMessageBox.information(self, "No Path Found", "No path found between selected airports.")
                return
            for iata in bfs_route:
                airport_path = node_airport.get(iata)
                if airport_path:
                    text = f"Airport Name :{airport_path.name} Airport Code :{airport_path.iata_code}"
                    folium.Marker(location=[airport_path.latitude, airport_path.longitude], popup=text,
                                  icon=folium.Icon(color="green")).add_to(airport_map)
                    bfs_coords.append((airport_path.latitude, airport_path.longitude))
                folium.plugins.AntPath(locations=bfs_coords, color="blue", weight=2.5, opacity=1).add_to(airport_map)

        if self.cost_checkbox.isChecked():
            cost_path = airport_graph.cheapest_flight_astar(source_iata, destination_iata)
            cost_coords = []
            cost_route, cost_of_flight = cost_path
            if cost_route is None:
                QMessageBox.information(self, "No Path Found", "No path found between selected airports")
            for iata in cost_route:
                airport_path = node_airport.get(iata)
                if airport_path:
                    text = f"Airport Name :{airport_path.name} Airport Code :{airport_path.iata_code}"
                    folium.Marker(location=[airport_path.latitude, airport_path.longitude], popup=text,
                                  icon=folium.Icon(color="pink")).add_to(airport_map)
                    cost_coords.append((airport_path.latitude, airport_path.longitude))
                folium.plugins.AntPath(locations=cost_coords, color="pink", weight=2.5, opacity=0.5).add_to(airport_map)

        airport_map.save('airport_map.html')
        self.web_view.setHtml(open("airport_map.html").read())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MapWindow()
    window.show()
    sys.exit(app.exec_())
