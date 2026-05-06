mod routes;
mod service;
fn main() { actix_web::HttpServer::new(|| {
    actix_web::App::new().configure(routes::config)
}).bind("127.0.0.1:8080").unwrap().run().unwrap(); }
