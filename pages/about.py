import dash
from dash import html, dcc, clientside_callback, Input, Output
import dash_bootstrap_components as dbc

dash.register_page(__name__)

layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        dbc.Container(
            [
                dbc.Row(
                    [
                        # Table of Contents Sidebar
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        html.H5(
                                            "Table of Contents",
                                            className="mb-3",
                                            style={"color": "#495057"},
                                        ),
                                        html.Ul(
                                            [
                                                html.Li(
                                                    [
                                                        html.A(
                                                            "Overview",
                                                            href="#overview",
                                                            className="toc-link",
                                                        )
                                                    ]
                                                ),
                                                html.Li(
                                                    [
                                                        html.A(
                                                            "Model Description",
                                                            href="#model",
                                                            className="toc-link",
                                                        )
                                                    ]
                                                ),
                                                html.Li(
                                                    [
                                                        html.A(
                                                            "Model Calibration Strategies",
                                                            href="#calibration",
                                                            className="toc-link",
                                                        )
                                                    ]
                                                ),
                                                html.Li(
                                                    [
                                                        html.A(
                                                            "Technical Details",
                                                            href="#technical",
                                                            className="toc-link",
                                                        )
                                                    ]
                                                ),
                                                html.Li(
                                                    [
                                                        html.A(
                                                            "Source Code & Data",
                                                            href="#source",
                                                            className="toc-link",
                                                        )
                                                    ]
                                                ),
                                            ],
                                            className="list-unstyled toc-list",
                                        ),
                                    ],
                                    className="toc-sidebar",
                                    style={
                                        "position": "sticky",
                                        "top": "80px",
                                        "background": "#f8f9fa",
                                        "padding": "20px",
                                        "border-radius": "8px",
                                        "border": "1px solid #dee2e6",
                                    },
                                )
                            ],
                            width=3,
                            className="d-none d-md-block",
                        ),
                        # Main Content
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        # Overview Section
                                        html.Div(
                                            [
                                                html.H2(
                                                    "Overview",
                                                    id="overview",
                                                    className="section-heading",
                                                ),
                                                html.P(
                                                    [
                                                        "This dashboard serves model output, water balance components, and station data from instrumented ",
                                                        "groundwater wells in the Dangermond Preserve. The Dangermond Preserve is a 24,364-acre ",
                                                        "coastal ranch in Santa Barbara County, California, that was purchased by The Nature Conservancy ",
                                                        "to protect critical wildlife corridors and coastal ecosystems.",
                                                    ]
                                                ),
                                                html.P(
                                                    [
                                                        "The primary use of this dashboard is to visualize model results from CFE (Conceptual Functional Equivalent), ",
                                                        "a conceptual hydrologic model that offers a Basic Model Interface (BMI) compatible version of the National Water Model. ",
                                                        "The dashboard serves as an entry point to the data, visualizing monthly aggregations of water balance variables, ",
                                                        "observations, and forcing variables.",
                                                    ]
                                                ),
                                                html.P(
                                                    [
                                                        "Users can explore relationships between precipitation, evapotranspiration, soil moisture, and groundwater levels ",
                                                        "across different monitoring locations within the preserve. The dashboard currently displays a subset of the data available"
                                                        " from this project, focusing on CFE results from an experimental groundwater calibration effort. The full suite of data products—which includes model output, hydroclimatic variables summarized to the Preserve catchments, and station data collected from various sources—is described in the data repository README. A general overview of the project is provided below.",
                                                    ]
                                                ),
                                            ],
                                            className="content-section",
                                        ),
                                        # # Purpose Section
                                        # html.Div(
                                        #     [
                                        #         html.H2(
                                        #             "Dashboard Purpose",
                                        #             id="purpose",
                                        #             className="section-heading",
                                        #         ),
                                        #         html.P(
                                        #             [
                                        #                 "The primary use of this dashboard is to visualize model results from CFE (Conceptual Functional Equivalent), ",
                                        #                 "a conceptual hydrologic model that offers a Basic Model Interface (BMI) compatible version of the National Water Model. ",
                                        #                 "The dashboard serves as an entry point to the data, visualizing monthly aggregations of water balance variables, ",
                                        #                 "observations, and forcing variables.",
                                        #             ]
                                        #         ),
                                        #         html.P(
                                        #             [
                                        #                 "Users can explore relationships between precipitation, evapotranspiration, soil moisture, and groundwater levels ",
                                        #                 "across different monitoring locations within the preserve.",
                                        #             ]
                                        #         ),
                                        #     ],
                                        #     className="content-section",
                                        # ),
                                        # Model Section
                                        html.Div(
                                            [
                                                html.H2(
                                                    "Model Description",
                                                    id="model",
                                                    className="section-heading",
                                                ),
                                                html.P(
                                                    [
                                                        "To support a modular approach to hydrologic modeling across the preserve and leverage existing data and tools, Lynker applied the flexible NextGen multi-modeling framework to run the Conceptual-Functional Equivalent (CFE)  hydrologic model across the study area. CFE is a rainfall-runoff model that is an conceptual implementation of the operational US National Water Model. CFE is a semi-distributed model, where the domain is discretized by sub-basin catchment boundaries, and runoff generation, groundwater storage, and vadose zone fluxes are defined by conceptual reservoirs. Forcings are distributed to these catchments on an hourly timestep. CFE surface water outflow is routed into streamflow using the t-route  channel routing model."
                                                    ]
                                                ),
                                                html.P(
                                                    [
                                                        "CFE is a simplified hydrologic model that maintains the core water balance functionality of more complex models while being computationally efficient. ",
                                                    ]
                                                ),
                                                html.P(
                                                    [
                                                        "Key features:",
                                                    ]
                                                ),
                                                html.Ul(
                                                    [
                                                        html.Li(
                                                            "Basic Model Interface (BMI) compatibility"
                                                        ),
                                                        html.Li(
                                                            "Water balance calculations for soil moisture and groundwater"
                                                        ),
                                                        html.Li(
                                                            "Evapotranspiration estimation"
                                                        ),
                                                        html.Li(
                                                            "Surface and subsurface flow routing"
                                                        ),
                                                    ]
                                                ),
                                                html.P(
                                                    [
                                                        "Forcing data for CFE is sourced from NOAA's Analysis Of Record for Calibration (AORC) dataset, which provides an hourly gridded record of near-surface weather conditions at an 800 m spatial resolution across the continental US from 1979 to present. AORC variables include total precipitation, temperature, specific humidity, terrain-level pressure, downward longwave and shortwave radiation, and wind vectors."
                                                    ]
                                                ),
                                            ],
                                            className="content-section",
                                        ),
                                        # Station Data
                                        html.Div(
                                            [
                                                html.H2(
                                                    "Station Data Summary",
                                                    id="station-data",
                                                    className="section-heading",
                                                ),
                                                html.P(
                                                    [
                                                        "To prepare in situ data for model calibration and verification, Lynker developed a suite of QA/QC methods and routines, with specific attention on the high density of pressure transducer data, which was primarily supplied as raw datalogger output. Unprocessed, raw pressure transducer data can contain noise, spikes, sensor drift, or water sampling events which must be postprocessed to develop a clean time series. Legacy groundwater level data are available across most sites for two periods, 2010-2011 and 2021-2022. "
                                                    ]
                                                ),
                                                html.P(
                                                    [
                                                        "Jalama Creek (USGS-11120600) flows from the 1965-1980 period of record shows peak flows around ~28 m3 s-1, or ~1,000 cfs. Around 80% of days had detected flows suggesting a near-perennial stream, but only 40% of days had flows greater than ~0.01 m3 s-1. Low flows are difficult to accurately gage and can be an artifact of the rating curve development or measurement methods. These observations reflect the flashy nature of waterways in coastal California, where the highest flows occur during the winter rainy season, and summer months are markedly dry. Jalama Creek exhibits very low flows for much of the year. In this Mediterranean climate, event-based streamflow generation drives high discharge (e.g., winter atmospheric river events are a significant contributor) while baseflow conditions prevail outside of the winter rainy season. The low elevation and geography of the domain prevents any meaningful snowfall accumulation."
                                                    ]
                                                ),
                                                html.P(
                                                    [
                                                        "Streamflow observations from the basin outlet (USGS gauge 11120600) are available only up to 1980. To provide a basis for model evaluation after 1980, we identified a nearby gauge (USGS gauge 11132500) located approximately 12km from the Jalama Creek gauge in the Salsipuedes Creek basin on the northeast border of the Preserve. Elevational distribution and areas between the two basins were largely similar, and the correlation between the two records was high (r2 = 0.88), enabling a regression-based flow estimation for Jalama Creek throughout the validation period."
                                                    ]
                                                ),
                                            ],
                                            className="content-section",
                                        ),
                                        # Model Calibration
                                        html.Div(
                                            [
                                                html.H2(
                                                    "Model Calibration Strategies",
                                                    id="calibration",
                                                    className="section-heading",
                                                ),
                                                html.P(
                                                    [
                                                        "We developed and tested two independent calibration strategies. The first calibration targeted streamflow at the domain outlet on Jalama Creek, using the available USGS observations for the period 1979-10-01 to 1982-09-28. The second calibration strategy aimed to leverage the groundwater data available in the preserve. This experimental strategy used observed well water levels to calibrate parameters controlling the subsurface fluxes. Both calibration strategies optimized model parameters for 300 iterations."
                                                    ]
                                                ),
                                                # html.H4(
                                                #     "Groundwater Calibration Focus",
                                                #     className="mt-4 mb-3",
                                                # ),
                                                html.P(
                                                    [
                                                        "The second experimental calibration strategy focuses on groundwater in the preserve. Of the available groundwater data, Catchment-53, in the Northwestern hills of the preserve had the longest continuous record with several simultaneous water level data records in 2010-2011. Catchment-53, known as La Tinta basin, drains into Gasper Creek. The catchment sits between 1,000 and 1,700 feet MSL with an area of 2.3 km². Five groundwater wells exist in this catchment, although the record does not contain simultaneous data for all locations for all periods. One well (Tinta4) was used as a calibration target for the period between December 2009 and May 2011 where data is available."
                                                    ]
                                                ),
                                                html.P(
                                                    [
                                                        "Change in groundwater level is calculated as the difference between two fluxes that CFE uses to simulate subsurface dynamics: soil to groundwater flux and deep groundwater to channel flux. The difference between these conceptual reservoirs is the change in simulated groundwater storage at each timestep."
                                                    ]
                                                ),
                                            ],
                                            className="content-section",
                                        ),
                                        # Technical Details Section
                                        html.Div(
                                            [
                                                html.H2(
                                                    "Technical Details",
                                                    id="technical",
                                                    className="section-heading",
                                                ),
                                                html.P(
                                                    [
                                                        "The ",
                                                        html.A(
                                                            "summary memo",
                                                            href="https://your-link-here",
                                                            target="_blank",
                                                            className="text-primary",
                                                        ),
                                                        " contains additional details on the NextGen Framework, CFE, calibration strategies, and interpretation of results. ",
                                                    ]
                                                ),
                                            ],
                                            className="content-section",
                                        ),
                                        # Source Code Section
                                        html.Div(
                                            [
                                                html.H2(
                                                    "Source Code & Data Access",
                                                    id="source",
                                                    className="section-heading",
                                                ),
                                                html.H4(
                                                    "Data & Model Products",
                                                    className="mt-4 mb-3",
                                                ),
                                                html.Ul(
                                                    [
                                                        html.Li(
                                                            [
                                                                html.Strong(
                                                                    "Hydrofabric"
                                                                ),
                                                                html.Ul(
                                                                    [
                                                                        html.Li(
                                                                            "Geospatial inputs for hydrologic models (e.g., DEM, slope, aspect, flow direction)"
                                                                        )
                                                                    ]
                                                                ),
                                                            ]
                                                        ),
                                                        html.Li(
                                                            [
                                                                html.Strong(
                                                                    "Station Metadata & Maps"
                                                                ),
                                                            ]
                                                        ),
                                                        html.Li(
                                                            [
                                                                html.Strong(
                                                                    "Groundwater Data (groundwater/)"
                                                                ),
                                                                html.Ul(
                                                                    [
                                                                        html.Li(
                                                                            "Hourly, daily, and monthly groundwater levels"
                                                                        ),
                                                                        # html.Li(
                                                                        #     "Includes quality-controlled data and hourly differences"
                                                                        # ),
                                                                        # html.Li(
                                                                        #     "Used for calibration and analysis of subsurface hydrology"
                                                                        # ),
                                                                    ]
                                                                ),
                                                            ]
                                                        ),
                                                        html.Li(
                                                            [
                                                                html.Strong(
                                                                    "Meteorological Station Data (met_station_data/)"
                                                                ),
                                                                html.Ul(
                                                                    [
                                                                        html.Li(
                                                                            "Time series of weather observations stored in Parquet format"
                                                                        )
                                                                    ]
                                                                ),
                                                            ]
                                                        ),
                                                        html.Li(
                                                            [
                                                                html.Strong(
                                                                    "NextGen Model Data (ngen_dr/)"
                                                                ),
                                                                html.Ul(
                                                                    [
                                                                        html.Li(
                                                                            "Calibration, validation, and forcing data for CFE"
                                                                        ),
                                                                        html.Li(
                                                                            "Includes model outputs and specialized hydrofabric for simulation"
                                                                        ),
                                                                    ]
                                                                ),
                                                            ]
                                                        ),
                                                        html.Li(
                                                            [
                                                                html.Strong(
                                                                    "Hydrofabric Reference Data"
                                                                ),
                                                                html.Ul(
                                                                    [
                                                                        html.Li(
                                                                            "Alternative or refactored versions of hydrofabric for routing or modeling experiments"
                                                                        )
                                                                    ]
                                                                ),
                                                            ]
                                                        ),
                                                        html.Li(
                                                            [
                                                                html.Strong(
                                                                    "TNC Datastreams (tnc_datastreams/)"
                                                                ),
                                                                html.Ul(
                                                                    [
                                                                        html.Li(
                                                                            "Sensor data mirrored from the Dendra platform"
                                                                        ),
                                                                        html.Li(
                                                                            "Accessed using a custom API wrapper and stored as Parquet files"
                                                                        ),
                                                                    ]
                                                                ),
                                                            ]
                                                        ),
                                                        html.Li(
                                                            [
                                                                html.Strong(
                                                                    "Water Balance Data (water_balance/)"
                                                                ),
                                                                html.Ul(
                                                                    [
                                                                        html.Li(
                                                                            "Modeled components from:"
                                                                        ),
                                                                        html.Ul(
                                                                            [
                                                                                html.Li(
                                                                                    "CABCM: AET, PET, runoff, recharge, etc."
                                                                                ),
                                                                                html.Li(
                                                                                    "TerraClimate: temperature, PDSI, snow, vapor pressure, etc."
                                                                                ),
                                                                                html.Li(
                                                                                    "TNC: weighted Natural Flow predictions"
                                                                                ),
                                                                            ]
                                                                        ),
                                                                    ]
                                                                ),
                                                            ]
                                                        ),
                                                    ]
                                                ),
                                                html.H4(
                                                    "Source Code",
                                                    className="mt-4 mb-3",
                                                ),
                                                html.P(
                                                    [
                                                        "The source code for this application is available on GitHub: ",
                                                        html.A(
                                                            "Dangermond Web App Repository",
                                                            href="https://your-link-here",
                                                            target="_blank",
                                                            className="text-primary",
                                                        ),
                                                        ". The repository contains:",
                                                    ]
                                                ),
                                                html.Ul(
                                                    [
                                                        html.Li(
                                                            "Complete dashboard source code"
                                                        ),
                                                        html.Li(
                                                            "Data processing scripts for monthly aggregations"
                                                        ),
                                                        html.Li(
                                                            "Volume calculation methods"
                                                        ),
                                                        html.Li(
                                                            "Summary statistics generation code"
                                                        ),
                                                        html.Li(
                                                            "Documentation and setup instructions"
                                                        ),
                                                    ]
                                                ),
                                            ],
                                            className="content-section",
                                        ),
                                    ],
                                    className="main-content",
                                )
                            ],
                            width=9,
                        ),
                    ]
                )
            ],
            fluid=True,
            className="about-page",
            id="about-page-container",
        ),
    ]
)

# Clientside callback for TOC active link highlighting
clientside_callback(
    """
    function(pathname) {
        // Function to update active TOC link based on scroll position
        function updateActiveTOCLink() {
            const mainContent = document.querySelector('.main-content');
            const sections = document.querySelectorAll('.section-heading');
            const tocLinks = document.querySelectorAll('.toc-link');
            
            if (!mainContent || sections.length === 0) return;
            
            let current = '';
            const scrollTop = mainContent.scrollTop;
            
            sections.forEach(section => {
                const sectionTop = section.offsetTop - 50; // Offset for better UX
                if (scrollTop >= sectionTop) {
                    current = section.getAttribute('id');
                }
            });
            
            // Default to first section if no section is active
            if (!current && sections.length > 0) {
                current = sections[0].getAttribute('id');
            }
            
            tocLinks.forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === '#' + current) {
                    link.classList.add('active');
                }
            });
        }
        
        // Function to handle TOC link clicks for smooth scrolling
        function handleTOCClick() {
            const tocLinks = document.querySelectorAll('.toc-link');
            const mainContent = document.querySelector('.main-content');
            
            tocLinks.forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    const targetId = this.getAttribute('href').substring(1);
                    const targetElement = document.getElementById(targetId);
                    
                    if (targetElement && mainContent) {
                        const offsetTop = targetElement.offsetTop - 20;
                        mainContent.scrollTo({
                            top: offsetTop,
                            behavior: 'smooth'
                        });
                    }
                });
            });
        }
        
        // Update on page load
        setTimeout(() => {
            updateActiveTOCLink();
            handleTOCClick();
        }, 100);
        
        // Update on main content scroll
        const mainContent = document.querySelector('.main-content');
        if (mainContent) {
            mainContent.addEventListener('scroll', updateActiveTOCLink);
        }
        
        return window.dash_clientside.no_update;
    }
    """,
    Output("about-page-container", "children", allow_duplicate=True),
    Input("url", "pathname"),
    prevent_initial_call=True,
)
