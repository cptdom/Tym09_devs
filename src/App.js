import './App.css';
import Layout from './Layout/Layout';
import {Route,Switch} from 'react-router-dom';
import Intro from './Components/Intro';

function App() {
  return (
      <Layout>
        <Switch>
          <Route path="/" component={Intro}></Route>
        </Switch>
      </Layout>
  );
}

export default App;
