// Smooth section animations
document.addEventListener("DOMContentLoaded", () => {
    const sections = document.querySelectorAll("section, .glass-card");
    sections.forEach((el, index) => {
        el.style.opacity = 0;
        el.style.transform = "translateY(30px)";
        setTimeout(() => {
            el.style.transition = "all 0.8s ease";
            el.style.opacity = 1;
            el.style.transform = "translateY(0)";
        }, index * 200);
    });
});
