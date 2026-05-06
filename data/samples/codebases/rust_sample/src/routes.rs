use actix_web::{get, post, web};
use crate::service;
#[get("/items")]
async fn list_items() -> web::Json<Vec<String>> { web::Json(service::list_all()) }
#[post("/items")]
async fn create_item() -> web::Json<String> { web::Json(service::create()) }
pub fn config(cfg: &mut web::ServiceConfig) { cfg.service(list_items).service(create_item); }
