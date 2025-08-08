import { Title, Container, Main } from '../../components'
import styles from './styles.module.css'
import MetaTags from 'react-meta-tags'

const About = ({ updateOrders, orders }) => {
  
  return <Main>
    <MetaTags>
      <title>О проекте</title>
      <meta name="description" content="Фудграм - О проекте" />
      <meta property="og:title" content="О проекте" />
    </MetaTags>
    
    <Container>
      <h1 className={styles.title}>Привет!</h1>
      <div className={styles.content}>
        <div>
          <h2 className={styles.subtitle}>Что это за сайт?</h2>
          <div className={styles.text}>
            <p className={styles.textItem}>
              Foodgram - это ваша цифровая кулинарная книга и сообщество единомышленников. 
              Здесь вы найдете все необходимое для удобного планирования своего питания.
                <ul>
                  <li className={styles.textItem}>
                    Создавать и хранить свои рецепты
                  </li>
                  <li className={styles.textItem}>
                    Формировать списки покупок для любых блюд
                  </li>
                  <li className={styles.textItem}>
                    Следить за рецептами других пользователей
                  </li>
                  <li className={styles.textItem}>
                    Сохранять понравившиеся рецепты в избранное
                  </li>
                </ul>
            </p>
            <p className={styles.textItem}>
              Чтобы использовать все возможности сайта — нужна простая регистрация за 1 минуту - проверка email не требуется. 
              После входа вы получите полный доступ ко всем возможностям сервиса.
            </p>
            <p className={styles.textItem}>
              Заходите и делитесь своими любимыми рецептами уже сегодня! Вдохновляйтесь рецептами других пользователей и сделайте процесс готовки еще удобнее.
            </p>
          </div>
        </div>
        <aside>
          <h2 className={styles.additionalTitle}>
            Ссылки
          </h2>
          <div className={styles.text}>
            <p className={styles.textItem}>
              Код проекта находится тут - <a href="https://github.com/Kamilla-ElhDaou/foodgram.git" className={styles.textLink}>Github</a>
            </p>
            <p className={styles.textItem}>
              Автор проекта: <a href="https://t.me/liaklam" className={styles.textLink}>Эль Хадж Дау Камилла</a>
            </p>
          </div>
        </aside>
      </div>
      
    </Container>
  </Main>
}

export default About

