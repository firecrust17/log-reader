import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class DataService {

  constructor(private http: HttpClient) { }

  fetch_file_list() {
    const endpoint = 'http://localhost:5000/fs/ls_files';
    return this.http.get<DataService>(endpoint);
  }

  retrieve_logs(version: String) {
    const endpoint = 'http://localhost:5000/search/search_log/'+version;
    return this.http.get<DataService>(endpoint);
  }


}
