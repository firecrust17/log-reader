import { Component } from '@angular/core';
import { DataService } from './services/data.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {

  constructor(private ds: DataService) {
    this.init_payload();
    this.fetch_file_list();
  }

  title = 'log-viewer';
  active_btn: String = 'v3';
  payload: any;

  file_list = [];
  log_data = [];
  
  init_payload() {
    this.payload = {
      filename: null,
      keyword: "",
      count: 0,
      chunk_size: 100
    }
  }

  setActive(btn: String){
    this.active_btn = btn;
  }

  search(){
    if(this.payload.filename == null){
      alert("File name is Mandatory!");
    }
    this.ds.retrieve_logs(this.active_btn)
    .subscribe((res: any) =>{
      this.log_data = res.data;
    });
  }

  fetch_file_list() {
    this.ds.fetch_file_list()
    .subscribe((res: any) =>{
      this.log_data = res.data;
    });
  }

}
