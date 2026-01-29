import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { GenerationPage } from "./GenerationPage";
import ResultsPage from "./ResultsPage";
import InputPage from "./InputPage";

export function App(){
  // return (<>ahjsdajsgd</>)
  return (
    <Router>
      <Routes>
        <Route path="/" element={<InputPage />} />
        <Route path="/generating" element={<GenerationPage />} />
        <Route path="/results" element={<ResultsPage />} />
      </Routes>
    </Router>
  );
};
