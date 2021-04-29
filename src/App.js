import './App.css';
import Layout from './Layout/Layout';
import {Route,Switch} from 'react-router-dom';
import Intro from './Components/navbar_left/Intro';
import About from './Components/navbar_left/About';
import Pricing from './Components/navbar_left/Pricing';
import Contact from './Components/navbar_left/Contact';
import Product from './Components/navbar_left/Product';


function App() {
  return (
      <Layout>
        <Switch>
          <Route path="/product" component={Product}></Route>
          <Route path="/about" component={About}></Route>
          <Route path="/pricing" component={Pricing}></Route>
          <Route path="/contact" component={Contact}></Route>
          <Route path="/" component={Intro}></Route>
        </Switch>
      </Layout>
  );
}

export default App;
