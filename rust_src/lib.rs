use pyo3::prelude::*;
use pyo3::types::PyModule;
use egg::*;
use std::collections::HashMap;

#[pyclass]
#[derive(Clone)]
struct PyIteration {
    #[pyo3(get)]
    pub nodes: usize,
    #[pyo3(get)]
    pub eclasses: usize,
    #[pyo3(get)]
    pub time: f64,
}

#[pyclass]
struct RustEGraph {
    egraph: EGraph<SymbolLang, ()>,
}

#[pymethods]
impl RustEGraph {
    #[new]
    fn new() -> Self {
        RustEGraph {
            egraph: EGraph::default().with_explanations_enabled(),
        }
    }

    fn add(&mut self, expr: &str) -> PyResult<()> {
        let parsed: RecExpr<SymbolLang> = expr.parse().map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Parse error: {}", e)))?;
        self.egraph.add_expr(&parsed);
        Ok(())
    }

    #[pyo3(signature = (rules, iterations=None))]
    fn run(&mut self, rules: Vec<(String, String, String)>, iterations: Option<usize>) -> PyResult<Vec<PyIteration>> {
        let mut rewrites = Vec::new();
        for (name, lhs, rhs) in rules {
            let searcher: Pattern<SymbolLang> = lhs.parse().map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("LHS parse error: {}", e)))?;
            let applier: Pattern<SymbolLang> = rhs.parse().map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("RHS parse error: {}", e)))?;
            let rewrite = Rewrite::new(name, searcher, applier).map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Rewrite creation error: {}", e)))?;
            rewrites.push(rewrite);
        }

        let mut runner = Runner::default()
            .with_explanations_enabled()
            .with_egraph(std::mem::take(&mut self.egraph));

        if let Some(limit) = iterations {
             runner = runner.with_iter_limit(limit);
        }

        runner = runner.run(&rewrites);

        let py_iterations = runner.iterations.iter().map(|iter| {
            PyIteration {
                nodes: iter.egraph_nodes,
                eclasses: iter.egraph_classes,
                time: iter.total_time,
            }
        }).collect();

        self.egraph = runner.egraph;
        Ok(py_iterations)
    }

    fn best(&self, expr: &str) -> PyResult<String> {
        self.extract(expr, "size")
    }

    fn extract(&self, expr: &str, cost: &str) -> PyResult<String> {
        let parsed: RecExpr<SymbolLang> = expr.parse().map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Parse error: {}", e)))?;
        let id = self.egraph.lookup_expr(&parsed).ok_or_else(|| PyErr::new::<pyo3::exceptions::PyValueError, _>("Expression not found in e-graph"))?;

        match cost {
            "size" => {
                let extractor = Extractor::new(&self.egraph, AstSize);
                let (_cost, best) = extractor.find_best(id);
                Ok(best.to_string())
            }
            "depth" => {
                let extractor = Extractor::new(&self.egraph, AstDepth);
                let (_cost, best) = extractor.find_best(id);
                Ok(best.to_string())
            }
            _ => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Unknown cost function: {}", cost)))
        }
    }

    fn are_equal(&self, expr1: &str, expr2: &str) -> PyResult<bool> {
        let parsed1: RecExpr<SymbolLang> = expr1.parse().map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Parse error expr1: {}", e)))?;
        let parsed2: RecExpr<SymbolLang> = expr2.parse().map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Parse error expr2: {}", e)))?;

        let id1 = self.egraph.lookup_expr(&parsed1);
        let id2 = self.egraph.lookup_expr(&parsed2);

        match (id1, id2) {
            (Some(i1), Some(i2)) => Ok(i1 == i2),
            _ => Ok(false),
        }
    }

    fn explain(&mut self, expr: &str) -> PyResult<String> {
        let parsed: RecExpr<SymbolLang> = expr.parse().map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Parse error: {}", e)))?;
        let id = self.egraph.lookup_expr(&parsed).ok_or_else(|| PyErr::new::<pyo3::exceptions::PyValueError, _>("Expression not found in e-graph"))?;

        let mut explanation = self.egraph.explain_equivalence(&parsed, &self.egraph.id_to_expr(id));
        Ok(explanation.get_flat_string())
    }

    fn why_equal(&mut self, a: &str, b: &str) -> PyResult<String> {
        let parsed_a: RecExpr<SymbolLang> = a.parse().map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Parse error a: {}", e)))?;
        let parsed_b: RecExpr<SymbolLang> = b.parse().map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Parse error b: {}", e)))?;

        // Ensure both expressions are present in the EGraph
        let id_a = self.egraph.lookup_expr(&parsed_a).ok_or_else(|| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Expression '{}' not found in e-graph", a)))?;
        let id_b = self.egraph.lookup_expr(&parsed_b).ok_or_else(|| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Expression '{}' not found in e-graph", b)))?;

        if id_a != id_b {
            return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Expressions '{}' and '{}' are not equal in the e-graph", a, b)));
        }

        let mut explanation = self.egraph.explain_equivalence(&parsed_a, &parsed_b);
        Ok(explanation.get_flat_string())
    }

    fn stats(&self) -> PyResult<HashMap<String, usize>> {
        let mut stats = HashMap::new();
        stats.insert("nodes".to_string(), self.egraph.total_size());
        stats.insert("classes".to_string(), self.egraph.number_of_classes());
        Ok(stats)
    }

    fn dump(&self) -> PyResult<String> {
        Ok(format!("{:?}", self.egraph))
    }
}

#[pymodule]
fn sie_core_rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<RustEGraph>()?;
    m.add_class::<PyIteration>()?;
    Ok(())
}
