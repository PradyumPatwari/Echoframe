document.addEventListener("DOMContentLoaded", () => {
    const cards = document.querySelectorAll(".team-card");
    cards.forEach((card, index) => {
        card.style.opacity = 0;
        card.style.transform = "translateY(20px)";
        setTimeout(() => {
            card.style.transition = "all 0.8s ease";
            card.style.opacity = 1;
            card.style.transform = "translateY(0)";
        }, index * 150);
    });
});
