import dash
from dash import html, dcc, clientside_callback, Input, Output
import dash_bootstrap_components as dbc

dash.register_page(__name__)

# Clientside callback for TOC active link highlighting
clientside_callback(
    """
    function(pathname) {
        // Function to update active TOC link based on scroll position
        function updateActiveTOCLink() {
            const sections = document.querySelectorAll('.section-heading');
            const tocLinks = document.querySelectorAll('.toc-link');
            
            let current = '';
            
            sections.forEach(section => {
                const sectionTop = section.offsetTop - 100; // Account for header
                if (window.scrollY >= sectionTop) {
                    current = section.getAttribute('id');
                }
            });
            
            tocLinks.forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === '#' + current) {
                    link.classList.add('active');
                }
            });
        }
        
        // Update on page load
        setTimeout(updateActiveTOCLink, 100);
        
        // Update on scroll
        window.addEventListener('scroll', updateActiveTOCLink);
        
        return window.dash_clientside.no_update;
    }
    """,
    Output("about-page-container", "children", allow_duplicate=True),
    Input("url", "pathname"),
    prevent_initial_call=True,
)

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
                                                            "Dashboard Purpose",
                                                            href="#purpose",
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
                                                            "Data Sources",
                                                            href="#data-sources",
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
                                                            "Source Code",
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
                                                        "This dashboard serves model output, historic water balance, and station data from instrumented ",
                                                        "groundwater wells in the Dangermond Preserve. The Dangermond Preserve is a 24,364-acre ",
                                                        "coastal ranch in Santa Barbara County, California, that was purchased by The Nature Conservancy ",
                                                        "in 2017 to protect critical wildlife corridors and coastal ecosystems.",
                                                    ]
                                                ),
                                            ],
                                            className="content-section",
                                        ),
                                        # Purpose Section
                                        html.Div(
                                            [
                                                html.H2(
                                                    "Dashboard Purpose",
                                                    id="purpose",
                                                    className="section-heading",
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
                                                        "across different monitoring locations within the preserve.",
                                                    ]
                                                ),
                                            ],
                                            className="content-section",
                                        ),
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
                                                        "The Conceptual Functional Equivalent (CFE) model is a simplified hydrologic model that maintains ",
                                                        "the core water balance functionality of more complex models while being computationally efficient. ",
                                                        "Key features include:",
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
                                            ],
                                            className="content-section",
                                        ),
                                        # Data Sources Section
                                        html.Div(
                                            [
                                                html.H2(
                                                    "Data Sources",
                                                    id="data-sources",
                                                    className="section-heading",
                                                ),
                                                html.P(
                                                    [
                                                        "The dashboard integrates multiple data sources to provide comprehensive hydrologic insights:"
                                                    ]
                                                ),
                                                html.Ul(
                                                    [
                                                        html.Li(
                                                            "Instrumented groundwater monitoring wells"
                                                        ),
                                                        html.Li(
                                                            "Weather station data (precipitation, temperature, wind)"
                                                        ),
                                                        html.Li(
                                                            "CFE model output (soil moisture, evapotranspiration, runoff)"
                                                        ),
                                                        html.Li(
                                                            "Historic water balance calculations"
                                                        ),
                                                    ]
                                                ),
                                                html.P(
                                                    [
                                                        "All data is aggregated to monthly timesteps for visualization purposes, though higher resolution ",
                                                        "data is available in the complete dataset.",
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
                                                        "The full data collection includes detailed descriptions of output variables, model parameters, ",
                                                        "calibration steps, and example code for reading output files. Monthly aggregations are calculated ",
                                                        "from daily model outputs, and summary statistics are provided for each monitoring location.",
                                                    ]
                                                ),
                                                html.P(
                                                    [
                                                        "Volume calculations are performed using standardized units and quality control procedures ",
                                                        "to ensure data reliability and consistency across different measurement periods.",
                                                    ]
                                                ),
                                            ],
                                            className="content-section",
                                        ),
                                        # Source Code Section
                                        html.Div(
                                            [
                                                html.H2(
                                                    "Source Code",
                                                    id="source",
                                                    className="section-heading",
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
