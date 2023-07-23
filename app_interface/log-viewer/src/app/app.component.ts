import { Component, OnInit } from '@angular/core';
import { DataService } from './services/data.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {

  constructor(private ds: DataService) {
    this.init_payload();
  }

  ngOnInit(): void {
    this.fetch_file_list();
  }

  title = 'log-viewer';
  active_btn: String = 'v3';
  payload: any;

  searchPerformed: boolean = false;
  isLoading: boolean = false;

  file_list: any = [];
  log_data = [];
  
  init_payload() {
    this.searchPerformed = false;
    this.payload = {
      filename: null,
      keyword: "",
      count: 10,
      chunk_size: 100
    }
  }

  setActive(btn: String){
    this.active_btn = btn;
  }

  search(){
    if(this.payload.filename == null){
      alert("File name is Mandatory!");
      return false;
    }
    this.searchPerformed = true;
    this.isLoading = true;
    let request:any  = this.payload
    if(request.keyword == '') delete(request.keyword)
    if(request.coumt == 0) delete(request.count)

    this.ds.retrieve_logs(this.active_btn, request)
    .subscribe((res: any) =>{
      this.log_data = res.data;
      this.isLoading = false;
    });
    return false;
  }

  fetch_file_list() {
    this.ds.fetch_file_list()
    .subscribe((res: any) =>{
      this.file_list = res;
    });
  }

}
