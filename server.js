// server.js (최종 수정 버전)

const express = require('express');
const xlsx = require('xlsx');
const path = require('path');

const app = express();
const port = 8080; // 또는 사용하시는 포트 번호

// 엑셀 파일을 읽어서 JSON으로 변환
const workbook = xlsx.readFile('data.xlsx');
const sheetName = workbook.SheetNames[0];
const sheet = workbook.Sheets[sheetName];

// ✍️ 이 부분이 수정되었습니다!
const headers = ['name', 'id', 'ramp', 'wheelchair', 'accessible_toilet', 'elevator', 'lat', 'lng'];
const placesData = xlsx.utils.sheet_to_json(sheet, { header: headers, range: 1 });


// '/api/places' 주소로 접속하면, 엑셀 데이터를 보내줌
app.get('/api/places', (req, res) => {
    res.json(placesData);
});

// 'public' 폴더를 사용하도록 설정
app.use(express.static(path.join(__dirname, 'public')));

// 서버 시작
app.listen(port, () => {
    console.log(`서버가 http://localhost:${port} 에서 실행 중입니다.`);
});