import './App.css';
import Layout from './Layout/Layout';
import { Route, Switch, Redirect } from 'react-router-dom';
import Intro from './Components/navbar_left/Intro';
import About from './Components/navbar_left/About';
//import Pricing from './Components/navbar_left/Pricing';
import Contact from './Components/navbar_left/Contact';
import Product from './Components/navbar_left/Product';
import Profile from './Components/profil/profil';
import Store from './store/store';


function App() {

  let state = Store.getState()

  return (
      <Layout>
        <Switch>
          <Route path="/profile" component={Profile}></Route>
          <Route path="/product" component={Product}></Route>
          <Route path="/about" component={About}></Route>
          {/* <Route path="/pricing" component={Pricing}></Route> */}
          <Route path="/contact" component={Contact}></Route>
          <Route path="/" component={Intro}></Route>
        </Switch>
      </Layout>
  );
}

export default App;
