function toggleMenu() {
    const menu = document.querySelector(".menu-links");
    const icon = document.querySelector(".hamburger-icon");
    menu.classList.toggle("open");
    icon.classList.toggle("open");
}

// ===== PROFILE IMAGE HOVER & CLICK EFFECT =====

const profilePic = document.getElementById('profilePic');
const image1 = document.getElementById('image1');
const image2 = document.getElementById('image2');
let isFirstImage = true;

if (profilePic) {
    // Ubah cursor jadi pointer
    profilePic.style.cursor = 'pointer';
    
    // Hover effect untuk smooth scale
    profilePic.addEventListener('mouseenter', function() {
        this.style.transform = 'scale(1.15)';
        this.style.transition = 'transform 1s ease';
    });
    
    profilePic.addEventListener('mouseleave', function() {
        this.style.transform = 'scale(1)';
    });

    // Click effect untuk toggle foto
    profilePic.addEventListener('click', function() {
        if (isFirstImage) {
            image1.classList.remove('active');
            image1.classList.add('inactive');
            image2.classList.remove('inactive');
            image2.classList.add('active');
        } else {
            image2.classList.remove('active');
            image2.classList.add('inactive');
            image1.classList.remove('inactive');
            image1.classList.add('active');
        }
        isFirstImage = !isFirstImage;
    });
}