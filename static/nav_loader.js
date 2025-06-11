// nav-loader.js
document.addEventListener("DOMContentLoaded", function() {
    // 1. nav.html 파일의 내용을 가져옵니다.
    fetch('../static/nav.html')
        .then(response => response.text())
        .then(data => {
            // 2. 가져온 내용을 id="nav-placeholder"를 가진 요소 안에 삽입합니다.
            document.getElementById('nav-placeholder').innerHTML = data;

            // 3. 현재 페이지의 경로를 가져옵니다. (예: "/award" 또는 "/work")
            // 만약 'www.gyumingim.kro.kr/award.html' 이라면 pathname은 '/award.html'이 됩니다.
            const currentPagePath = window.location.pathname;

            // 4. nav-placeholder 안의 모든 링크(<a> 태그)를 가져옵니다.
            const navLinks = document.querySelectorAll('#nav-placeholder a');

            navLinks.forEach(link => {
                // 5. 각 링크의 href 속성을 가져옵니다.
                const linkPath = new URL(link.href).pathname;

                // 6. 현재 페이지 경로와 링크 경로가 일치하는지 확인합니다.
                // 루트('/')의 경우, 'index.html' 또는 '/' 모두 일치하도록 처리합니다.
                if (currentPagePath === linkPath || (currentPagePath === '/' && linkPath.endsWith('/index.html'))) {
                    link.classList.add('active');
                }
            });
        })
        .catch(error => {
            console.error('Error loading navigation:', error);
        });
});