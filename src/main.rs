extern crate hyper;
extern crate rustc_serialize;
use hyper::Url;
use hyper::client::Client;
use rustc_serialize::json;
use std::io::Read;
use std::thread;

#[derive(RustcDecodable, RustcEncodable)]
pub struct Item {
    score: i32,
    title: String,
    url: String,
}

fn main() {
    // get list of best stories
    let client = Client::new();
    let mut response =
        client.get("https://hacker-news.firebaseio.com/v0/beststories.json").send().unwrap();
    let mut ids_str = String::new();
    response.read_to_string(&mut ids_str).unwrap();
    let ids: Vec<i32> = json::decode(&mut ids_str).unwrap();

    let mut joinhandles: Vec<std::thread::JoinHandle<()>> = Vec::new();

    // spawn threads to collect stories
    for id in ids {
        let joinhandle = thread::spawn(move || {
            let url_str: String = format!("https://hacker-news.firebaseio.com/v0/item/{}.json", id);
            let url = Url::parse(&url_str).unwrap();
            let client = Client::new();
            let mut response = client.get(url).send().unwrap();
            let mut item_str = String::new();
            response.read_to_string(&mut item_str).unwrap();
            let item: Item = json::decode(&mut item_str).unwrap();
            println!("{}\n  {}\n  {}\n", item.title, item.score, item.url);
        });

        joinhandles.push(joinhandle);
    }

    // wait for threads to finish
    for joinhandle in joinhandles {
        joinhandle.join().unwrap();
    }
}
