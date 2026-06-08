# kusa 7080 노래책

## 구조

```
mykusasong/
├── a.csv        # 노래 데이터
├── b.csv        # 노래 데이터
├── c.csv        # 노래 데이터
├── d.csv        # 노래 데이터
├── build.py     # index.html 생성 스크립트
└── index.html   # 빌드 결과물 (웹앱)
```

## CSV 파일 형식

각 CSV 파일의 컬럼 구조:

- **a/c/d.csv**: `장르, 제목, 빈칸, 기타코드, 가사`
- **b.csv**: `장르, 제목, 빈칸, 가사` (코드 컬럼 없음)

```
동요,가을,가을바람,C,"가을이라 가을 바람 솔솔 불어오니..."
```

## 곡 추가 방법

해당 CSV 파일에 한 행 추가:

```
장르,제목,,기타코드,"가사 내용
2번째 줄
3번째 줄"
```

가사가 여러 줄이면 큰따옴표로 감싼다.

## 빌드

CSV 수정 후 index.html 재생성:

```bash
python3 build.py
```

빌드 성공 시 출력 예시:
```
a.csv: 52곡
b.csv: 48곡
c.csv: 55곡
d.csv: 69곡
총 224곡 | 장르: 가요, 동요, 엣가요, 최신가요
생성 완료: /path/to/index.html
```

## Git 커밋

```bash
# 변경 파일 확인
git status

# 수정한 파일 스테이징 (예시)
git add d.csv index.html

# 커밋
git commit -m "곡 추가: 홍길동 - 아리랑"

# 원격 저장소에 푸시
git push
```

### 커밋 메시지 예시

```
Add guitar chords for 10 songs
곡 추가: 동요 5곡
Update lyrics for 가을
```
