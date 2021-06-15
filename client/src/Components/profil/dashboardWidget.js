import React, { Component } from 'react';
import tableau from 'tableau-api';
 
 
class DashboardWidget extends Component {
  componentDidMount() {
    this.initViz()
  }
 
 
  initViz() {
    const vizUrl = 'https://public.tableau.com/views/RealQuik2/Dashboard12?:language=en-US&:display_count=n&:origin=viz_share_link';
    const vizContainer = this.vizContainer;
    const options = {
        hideTabs: true,
        width: "1200px",
        height: "700px",
    }
    let viz = new window.tableau.Viz(vizContainer, vizUrl, options)
  }
 
 
  render() {
    return (
      <div ref={(div) => { this.vizContainer = div }}>
      </div>
    )
  }
}
 
 
export default DashboardWidget;